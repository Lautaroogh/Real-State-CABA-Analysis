import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

class ZonaPropScraper:
    def __init__(self):
        self.base_url = "https://www.zonaprop.com.ar"
        self.scraper = cloudscraper.create_scraper()
        self.data = []

    def get_listings(self, operation="venta", property_type="departamentos", location="capital-federal", max_pages=None, max_items=None):
        
        page = 1
        safety_limit = 3000 
        
        while True:
            if max_pages and page > max_pages:
                print(f"Reached requested max_pages limit: {max_pages}")
                break
            
            if page > safety_limit:
                print(f"Reached safety limit of {safety_limit} pages. Stopping.")
                break

            url = f"{self.base_url}/{property_type}-{operation}-{location}-pagina-{page}.html".replace("-pagina-1.html", ".html")
            print(f"Scraping Page {page}: {url}")
            
            try:
                time.sleep(random.uniform(3, 7))
                
                response = self.scraper.get(url)
                
                if response.status_code == 403:
                    print(f"Blocked (403) at {url} even with Cloudscraper.")
                    break
                
                if response.status_code != 200:
                    print(f"Stopping: Failed to retrieve {url} - Status: {response.status_code}")
                    break 
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if page > 1 and (f"-pagina-{page}.html" not in response.url and f"-pagina-1.html" not in url):
                     current_url = response.url
                     if f"-pagina-{page}" not in current_url and "pagina" not in current_url:
                         pass

                listings = soup.find_all('div', attrs={"data-qa": ["posting PROPERTY", "posting DEVELOPMENT"]})

                if not listings:
                    print(f"No listings found on page {page}. Stopping.")
                    break

                print(f"Found {len(listings)} listings on page {page}") 

                for item in listings:
                    try:
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

                        features = []
                        if features_elem:
                            spans = features_elem.find_all('span')
                            features = [s.text.strip() for s in spans]
                        
                        amenities = [a.text.strip() for a in amenities_elems] if amenities_elems else []
                        features.extend(amenities)


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

                        if max_items and len(self.data) >= max_items:
                            print(f"Reached limit of {max_items} items.")
                            return pd.DataFrame(self.data)
                        
                    except Exception as e:
                        print(f"Error parsing item: {e}")
                        continue
                
            except Exception as e:
                print(f"Error requesting {url}: {e}")
                break
            
            page += 1
                
        return pd.DataFrame(self.data)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape Real Estate listings from ZonaProp")
    parser.add_argument("--qty", type=int, default=0, help="Number of properties to scrape. Set to 0 for maximum available.")
    args = parser.parse_args()

    scraper = ZonaPropScraper()
    
    limit = args.qty if args.qty > 0 else None
    limit_msg = f"{limit}" if limit else "MAXIMUM"
    print(f"Starting scraper... Target: {limit_msg} properties.")

    df = scraper.get_listings(max_pages=None, max_items=limit)
    
    if not df.empty:
        print(df.head())
        output_path = "data/raw/real_estate_listings.csv"
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
    else:
        print("No data extracted. Check connection or headers.")
