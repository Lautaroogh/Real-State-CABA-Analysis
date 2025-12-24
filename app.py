import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Buenos Aires Real Estate", layout="wide")

st.title("Buenos Aires Real Estate Dashboard 🏢")

DATA_PATH = "data/processed/cleaned_listings.csv"

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    return pd.read_csv(DATA_PATH)

df = load_data()

if df is not None:
    st.sidebar.header("Filters")
    
    # Price Filter
    min_price, max_price = int(df['price_usd'].min()), int(df['price_usd'].max())
    price_range = st.sidebar.slider("Price Range (USD)", min_price, max_price, (min_price, max_price))
    
    filtered_df = df[
        (df['price_usd'] >= price_range[0]) & 
        (df['price_usd'] <= price_range[1])
    ]
    
    # Main KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Price", f"USD {filtered_df['price_usd'].mean():,.0f}")
    col2.metric("Listings Count", len(filtered_df))
    col3.metric("Min Price", f"USD {filtered_df['price_usd'].min():,.0f}")
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Price Distribution")
        fig_hist = px.histogram(filtered_df, x="price_usd", nbins=30, title="Price Histogram")
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with col_chart2:
        st.subheader("Price Boxplot")
        fig_box = px.box(filtered_df, y="price_usd", title="Price Boxplot")
        st.plotly_chart(fig_box, use_container_width=True)
        
    st.subheader("Raw Data")
    st.dataframe(filtered_df)

else:
    st.warning("No data found. Please run the scraper and cleaner first.")
    if st.button("Run Scraper (Demo)"):
        st.info("This would run the scraper script...")
        # In a real app, you might trigger the script here or use a database.
