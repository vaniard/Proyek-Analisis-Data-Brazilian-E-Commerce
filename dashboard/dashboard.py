import pandas as pd 
import seaborn as sns 
import streamlit as st 
import matplotlib.pyplot as plt 
import numpy as np  
import geopandas as gpd 

df = pd.read_csv("all_data.csv")

#Dashboard layout
st.title("E-commerce Data Dashboard")
st.markdown('<div style="text-align:justify">Brazilian E-commerce Public Dataset by Olist📊.</div>', unsafe_allow_html=True)

#Metode Pembayaran 
st.subheader("Metode Pembayaran Pelanggan")
fig, ax = plt.subplots(figsize=(10, 5))
sns.countplot(x='payment_type', data=df, order=df['payment_type'].value_counts().index)
plt.xticks(rotation=0)
st.pyplot(fig)

#Geospatial Analysis
geo_data = pd.read_csv("olist_geolocation_dataset.csv")
geodata = geo_data[['geolocation_lat', 'geolocation_lng']].dropna()
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(x=geodata['geolocation_lng'], y=geodata['geolocation_lat'], alpha=0.5)
st.pyplot(fig)

#Produk Kategori
category_counts = df['product_category_name'].value_counts()

fig, ax = plt.subplots(figsize=(12, 6))

sns.barplot(x=category_counts.index, y=category_counts.values, palette='viridis', ax=ax)

ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_xlabel('Product Category Name')
ax.set_ylabel('Jumlah Pembelian')
ax.set_title('Kategori Produk yang Paling Banyak Dibeli')

st.pyplot(fig)

#Harga Produk
st.subheader("Distribusi Harga Produk")
fig, ax = plt.subplots(figsize=(10,5))
sns.histplot(df['price'], bins=30, kde=True, ax=ax)
st.pyplot(fig)

st.subheader("Distribusi Status Pesanan")

fig, ax = plt.subplots (figsize=(12,6))

sns.countplot(x='order_status', data=df, order=df['order_status'].value_counts().index, ax=ax)

ax.set_title('Distribusi Status Pesanan')
ax.set_xlabel('Status Pesanan')
ax.set_ylabel('Jumlah Pesanan')
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

st.pyplot(fig)