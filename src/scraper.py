import cloudscraper
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

class ZonaPropScraper:
    def __init__(self):
        self.base_url = "https://www.zonaprop.com.ar"
        # Cloudscraper handles User-Agent and Cookies automatically to pass Cloudflare
        self.scraper = cloudscraper.create_scraper()
        self.data = []

    def get_listings(self, operation="venta", property_type="departamentos", location="capital-federal", max_pages=10):
        # ZonaProp URL structure: /departamentos-venta-capital-federal-pagina-2.html
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/{property_type}-{operation}-{location}-pagina-{page}.html".replace("-pagina-1.html", ".html")
            print(f"Scraping: {url}")
            
            try:
                # Add delay to be polite
                time.sleep(random.uniform(3, 7))
                
                response = self.scraper.get(url)
                
                if response.status_code == 403:
                    print(f"Blocked (403) at {url} even with Cloudscraper.")
                    break
                
                if response.status_code != 200:
                    print(f"Failed to retrieve {url} - Status: {response.status_code}")
                    break 
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Verified selector from HTML dump: <div data-qa="posting PROPERTY">
                listings = soup.find_all('div', attrs={"data-qa": ["posting PROPERTY", "posting DEVELOPMENT"]})

                # Debugging: Save HTML if no listings found
                if not listings:
                    print(f"DEBUG: No listings found. Saving HTML to 'debug_zonaprop.html' for inspection.")
                    with open("debug_zonaprop.html", "w", encoding="utf-8") as f:
                        f.write(soup.prettify())

                print(f"Found {len(listings)} listings on page {page}")

                for item in listings:
                    try:
                        # Verified verified data-qa
                        price_elem = item.find('div', attrs={'data-qa': 'POSTING_CARD_PRICE'})
                        location_elem = item.find('h2', attrs={'data-qa': 'POSTING_CARD_LOCATION'})
                        features_elem = item.find('h3', attrs={'data-qa': 'POSTING_CARD_FEATURES'})
                        expensas_elem = item.find('div', attrs={'data-qa': 'expensas'})
                        description_elem = item.find(['h3', 'div'], attrs={'data-qa': 'POSTING_CARD_DESCRIPTION'})
                        amenities_elems = item.find_all('span', class_=lambda x: x and 'pill-item-feature' in x)
                        
                        price = price_elem.text.strip() if price_elem else None
                        location_text = location_elem.text.strip() if location_elem else None
                        expensas = expensas_elem.text.strip() if expensas_elem else None
                        description = description_elem.text.strip() if description_elem else ""

                        # Features list
                        features = []
                        if features_elem:
                            spans = features_elem.find_all('span')
                            features = [s.text.strip() for s in spans]
                        
                        # Extra amenities (Parrilla, Pileta, etc.)
                        amenities = [a.text.strip() for a in amenities_elems] if amenities_elems else []
                        features.extend(amenities)



                        # URL is in the main container data-to-posting attribute
                        relative_url = item.get('data-to-posting')
                        full_url = self.base_url + relative_url if relative_url else None
                        
                        self.data.append({
                            'price': price,
                            'location': location_text,
                            'features': features,
                            'expensas': expensas,

                            'description': description[:200], 
                            'url': full_url
                        })
                        
                    except Exception as e:
                        print(f"Error parsing item: {e}")
                        continue
                
            except Exception as e:
                print(f"Error requesting {url}: {e}")
                break
                
        return pd.DataFrame(self.data)

if __name__ == "__main__":
    scraper = ZonaPropScraper()
    df = scraper.get_listings(max_pages=2)
    
    if not df.empty:
        print(df.head())
        output_path = "data/raw/real_estate_listings.csv"
        # Ensure directory exists just in case (though we ran mkdir)
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
    else:
        print("No data extracted. Check connection or headers.")
