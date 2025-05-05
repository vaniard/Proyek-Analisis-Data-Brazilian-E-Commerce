import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
from datetime import datetime

def load_data():
    data = pd.read_csv('all_df(1).csv')

    date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date', 'review_creation_date', 'review_answer_timestamp', 'shipping_limit_date']

    for col in date_cols:
        data[col] = pd.to_datetime(data[col], errors='coerce')

    data['purchase_to_delivery'] = (data['order_delivered_customer_date'] - data['order_purchase_timestamp']).dt.days
    data['estimated_vs_actual'] = (data['order_estimated_delivery_date'] - data['order_delivered_customer_date']).dt.days

    return data 

df = load_data()

st.title('Analisis Data Brazilian E-commerce')

st.sidebar.header('Filter Data')
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    [min_date, max_date],
    min_value = min_date,
    max_value = max_date
)

state_selected = st.sidebar.multiselect(
    'Pilih Negara Bagian',
    options = df['customer_state'].unique(),
    default = df['customer_state'].unique()
)

categories_selected = st.sidebar.multiselect(
    'Pilih Kategori Produk',
    options = df['product_category_name_english'].unique(),
    default = df['product_category_name_english'].unique()
)

df_filtered = df[
    (df['order_purchase_timestamp'].dt.date >= date_range[0]) & 
    (df['order_purchase_timestamp'].dt.date <= date_range[1]) &
    (df['customer_state'].isin(state_selected)) & 
    (df['product_category_name_english'].isin(categories_selected))
]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Rating", "Pengiriman", "Penjualan", "RFM"])

with tab1:
    st.header("Ringkasan Performa")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pesanan", df_filtered['order_id'].nunique())
    with col2:
        st.metric("Total Pelanggan", df_filtered['customer_unique_id'].nunique())
    with col3:
        avg_rating = df_filtered['review_score'].mean()
        st.metric("Rating Rata-rata", f"{avg_rating:.1f}")

    st.subheader("Distribusi Status Pesanan")
    payment_method = df_filtered['payment_type'].value_counts()
    fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
    ax_pie.pie(payment_method, labels=payment_method.index, autopct='%.0f%%', colors=plt.cm.Pastel1.colors, textprops={'fontsize': 10}, startangle=45)
    ax_pie.set_title('Distribusi Pembayaran Pelanggan', fontsize=12)
    st.pyplot(fig_pie)

    st.subheader("Metode Pembayaran")

    payment_counts = df_filtered['payment_type'].value_counts()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
    x=payment_counts.index,  
    y=payment_counts.values, 
    palette='pastel',
    ax=ax
    )
    ax.set_xlabel('Metode Pembayaran')
    ax.set_ylabel('Jumlah Order')
    ax.set_title('Metode Pembayaran yang Paling Disukai Pelanggan')

    plt.xticks(rotation=45)

    st.pyplot(fig)

    st.subheader("Produk Terbanyak dan Tersedikit Dibeli Pelanggan berdasarkan Total Pembelian")
    sum_order_items_df = df.groupby('product_category_name_english').order_id.nunique().sort_values(ascending=False).reset_index()

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
    colors = ['salmon', '#D3D3D3', '#D3D3D3', '#D3D3D3', '#D3D3D3']

    sns.barplot(x='order_id', y='product_category_name_english', data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("Produk Paling Banyak Dibeli", loc='center', fontsize=16)
    ax[0].tick_params(axis='y', labelsize=12)

    sns.barplot(x='order_id', y='product_category_name_english', data=sum_order_items_df.sort_values(by='order_id', ascending=True).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("Produk Paling Sedikit Dibeli", loc='center', fontsize=16)
    ax[1].tick_params(axis='y', labelsize=12)

    plt.suptitle('Produk Terbanyak dan Tersedikit Dibeli Pelanggan Berdasarkan Total Pembelian', fontsize=18)
    st.pyplot(fig)

with tab2:
    st.header("Analisis Rating Pelanggan")

    st.subheader("Distribusi Rating Pelanggan")
    review_score_counts = df.groupby("review_score").agg({"order_id": "nunique"}).sort_values(by="order_id", ascending=False).reset_index()

    fig_review, ax_review = plt.subplots(figsize=(7, 7))
    ax_review.pie(review_score_counts['order_id'], labels=review_score_counts['review_score'], autopct='%1.1f%%', startangle=90, textprops={'fontsize': 14})
    st.pyplot(fig_review)

    st.subheader("Pesanan berdasarkan Skor Ulasan")
    fig, ax = plt.subplots()
    sns.countplot(x=df["review_score"].dropna(), ax=ax, palette="Blues")
    ax.set_xlabel("Skor Ulasan")
    ax.set_ylabel("Jumlah Ulasan")
    st.pyplot(fig)

    st.subheader("Distribusi Rating")
    fig, ax = plt.subplots()
    sns.countplot(x='review_score', data=df_filtered, ax=ax)
    ax.set_xlabel('Rating (1.0 - 5.0)')
    ax.set_ylabel('Jumlah')
    st.pyplot(fig)

    st.subheader("Rating per Kategori Produk")
    category_rating = df_filtered.groupby('product_category_name_english')['review_score'].mean().sort_values(ascending=False)
    st.bar_chart(category_rating.head(10))

with tab3:
    st.header("Analisis Waktu Pengiriman")
    
    st.subheader("Rata-rata Waktu Pengiriman per Negara Bagian")
    state_delivery = df_filtered.groupby('customer_state')['purchase_to_delivery'].mean().sort_values()

    # Revised to match the histogram style below
    fig, ax = plt.subplots()
    state_delivery.plot(kind='bar', ax=ax, color='orange') 
    ax.set_xlabel("Negara Bagian")
    ax.set_ylabel("Rata-rata Hari Pengiriman")
    st.pyplot(fig)

    st.subheader("Rata-rata Waktu Pengiriman")
    df["delivery_time"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    fig, ax = plt.subplots()
    sns.histplot(df['delivery_time'].dropna(), bins=20, kde=True, ax=ax, color='orange')
    ax.set_xlabel("Hari Pengiriman")
    ax.set_ylabel("Jumlah Pesanan")
    st.pyplot(fig)

with tab4:
    st.header("Analisis Penjualan")
    
    st.subheader("Penjualan per Bulan")
    monthly_sales = df_filtered.set_index('order_purchase_timestamp').resample('M')['payment_value'].sum()
    st.line_chart(monthly_sales)

    st.subheader("Kategori Produk Terlaris")
    
    top_categories = df_filtered['product_category_name_english'].value_counts().head(10)

    fig, ax = plt.subplots()
    top_categories.plot(kind='bar', ax=ax, color='lightcoral')  # Changed to lightcoral to match
    ax.set_xlabel("Produk Kategori")
    ax.set_ylabel("Jumlah Pesanan")
    st.pyplot(fig)

    st.subheader("Penjualan berdasarkan Kategori Produk")
    kategori_penjualan = df.groupby("product_category_name_english")["price"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    kategori_penjualan.plot(kind="bar", ax=ax, color='lightcoral')
    ax.set_xlabel("Produk Kategori")
    ax.set_ylabel("Total Penjualan")
    st.pyplot(fig)
    
    st.subheader("Penjualan per Negara Bagian")
    
    state_sales = df_filtered.groupby('customer_state')['payment_value'].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    state_sales.plot(kind='bar', ax=ax, color='lightcoral')
    ax.set_xlabel("Negara Bagian")
    ax.set_ylabel("Total Penjualan")
    st.pyplot(fig)

    st.subheader('Distribusi Pelanggan dan Penjual berdasarkan Provinsi')
    customer_distribution = df['customer_state'].value_counts()
    seller_distribution = df['seller_state'].value_counts()

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))

    sns.barplot(x=customer_distribution.index, y=customer_distribution.values, ax=axes[0], palette="Blues_r")
    axes[0].set_title('Distribusi Pelanggan per Provinsi')
    axes[0].set_xlabel('Provinsi')
    axes[0].set_ylabel('Jumlah Pelanggan')

    sns.barplot(x=seller_distribution.index, y=seller_distribution.values, ax=axes[1], palette="Reds_r")
    axes[1].set_title('Distribusi Penjual per Provinsi')
    axes[1].set_xlabel('Provinsi')
    axes[1].set_ylabel('Jumlah Penjual')

    plt.tight_layout()
    st.pyplot(fig)

with tab5:
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'], errors='coerce')

    rfm_df = df.groupby(by='customer_id', as_index=False).agg({
        'order_approved_at': 'max',
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    rfm_df.columns = ['customer_id', 'max_order_approved_at', 'frequency', 'monetary']

    rfm_df['max_order_approved_at'] = pd.to_datetime(rfm_df['max_order_approved_at']).dt.date

    recent_date = df['order_approved_at'].dt.date.dropna().max()

    rfm_df = rfm_df.dropna(subset=['max_order_approved_at'])
    rfm_df['recency'] = rfm_df['max_order_approved_at'].apply(lambda x: (recent_date - x).days)

    rfm_df['customer_id'] = rfm_df['customer_id'].apply(lambda x: x[:8])

    st.subheader("Analisis RFM (Recency, Frequency, Monetary)")

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
    colors = ['#11b671'] * 5

    sns.barplot(y='recency', x='customer_id', data=rfm_df.sort_values(by='recency', ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title('By Recency', loc='center', fontsize=18)
    ax[0].tick_params(axis='x', labelsize=15)

    sns.barplot(y='frequency', x='customer_id', data=rfm_df.sort_values(by='frequency', ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title('By Frequency', loc='center', fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)

    sns.barplot(y='monetary', x='customer_id', data=rfm_df.sort_values(by='monetary', ascending=True).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title('By Monetary', loc='center', fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)

    plt.suptitle('Best Customer Based on RFM Parameters', fontsize=20)
    st.pyplot(fig)

    st.subheader("Clustering Pelanggan berdasarkan Provinsi")
    q1 = customer_distribution.quantile(0.25)
    q3 = customer_distribution.quantile(0.75)

    def categorize_cluster(value):
        if value <= q1:
            return "Low"
        elif value <= q3:
            return "Medium"
        else:
            return "High"

    customer_clusters = customer_distribution.apply(categorize_cluster)
    df_cluster = pd.DataFrame({
        "Provinsi": customer_distribution.index,
        "Jumlah Pelanggan": customer_distribution.values,
        "Cluster": customer_clusters.values
    })

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.scatterplot(x="Provinsi", y="Jumlah Pelanggan", hue="Cluster", palette={"Low": "gray", "Medium": "orange", "High": "green"}, data=df_cluster, s=100, ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.sidebar.header("Analisis Produk")
pencarian_product = st.sidebar.text_input("Cari Produk (ID atau Nama Kategori)")

if pencarian_product:
    product_results = df[
        (df['product_id'].str.contains(pencarian_product, case=False)) | 
        (df['product_category_name_english'].str.contains(pencarian_product, case=False))
    ]
    if not product_results.empty:
        st.sidebar.write(f"Ditemukan {len(product_results)} produk:")
        st.sidebar.dataframe(product_results[['product_id', 'product_category_name_english', 'price', 'review_score']].head(10))
    else:
        st.sidebar.write("Produk tidak ditemukan")