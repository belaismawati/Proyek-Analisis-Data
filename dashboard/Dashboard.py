# mengimpor library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import streamlit.components.v1 as components
import os

st.write("Current working dir:", os.getcwd())

# menyiapkan avg_rev_score
def create_avg_rev_score(df):
    avg_rev_score = df.groupby(by="product_category_name_english")["review_score"].mean().sort_values(ascending=False).reset_index()
    return avg_rev_score

# menyiapkan review_counts
def create_review_counts(df):
    review_counts = df.groupby(by="review_score").order_id.nunique().sort_values(ascending=False)
    return review_counts

# menyiapkan sum_orders_items_df
def create_sum_order_items_df(df):
    sum_order_items_df = df['product_category_name_english'].value_counts().reset_index()
    sum_order_items_df.columns = ['product_category_name_english', 'total_sales']
    return sum_order_items_df

# menyiapkan cust_bycity
def create_cust_bycity(df):
    cust_bycity = df.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=False)
    return cust_bycity

# menyiapkan cust_bystate
def create_cust_bystate(df):
    cust_bystate = df.groupby(by="customer_state").customer_id.nunique().sort_values(ascending=False)
    return cust_bystate

# menyiapkan seller_bycity
def create_seller_bycity(df):
    seller_bycity = df.groupby(by="seller_city").seller_id.nunique().sort_values(ascending=False)
    return seller_bycity

# menyiapkan seller_bystate
def create_seller_bystate(df):
    seller_bystate = df.groupby(by="seller_state").seller_id.nunique().sort_values(ascending=False)
    return seller_bystate

#  load berkas analisis_data.csv
# all_df = pd.read_excel("analisis_data.xls")

uploaded_file = st.file_uploader("Upload file", type=["xls", "xlsx"])

if uploaded_file is not None:
    all_df = pd.read_csv(uploaded_file)
    st.write(all_df.head())

    datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", 
                        "order_estimated_delivery_date", "shipping_limit_date", "review_creation_date", "review_answer_timestamp"]
    all_df.sort_values(by="order_purchase_timestamp", inplace=True) # mengurutkan DataFrame berdasarkan order_purchase_timestamp
    all_df.reset_index(inplace=True)

    # memastikan kolom tersebut bertipe datetime 
    for column in datetime_columns:
        all_df[column] = pd.to_datetime(all_df[column], errors='coerce')

    # membuat komponen filter
    min_date = all_df["order_purchase_timestamp"].min()
    max_date = all_df["order_purchase_timestamp"].max()

    with st.sidebar:
        # menambahkan logo perusahaan
        st.image("dashboard/Logo.png")

        # menambahkan judul sidebar
        st.title("🔍 Filter Data")

        # mengambil start_date & end_date dari date_input
        start_date, end_date = st.date_input(
            label='Rentang Waktu',min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

    # menyimpan data yang telah difilter ke main_df
    main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & (all_df["order_purchase_timestamp"] <= str(end_date))]

    avg_rev_score = create_avg_rev_score(main_df)
    review_counts = create_review_counts(main_df)
    sum_order_items_df = create_sum_order_items_df(main_df)
    cust_bycity = create_cust_bycity(main_df)
    cust_bystate = create_cust_bystate(main_df)
    seller_bycity = create_seller_bycity(main_df)
    seller_bystate = create_seller_bystate(main_df)

    # menambahkan header pada dashboard
    st.header('📊 Dashboard E-Commerce')

    # menambahkan sub-header pada dashboard
    st.subheader('📌 Ringkasan KPI')

    ## menampilkan informasi total order, rata-rata review skor, dan total produk dalam bentuk metric() 
    col1, col2, col3 = st.columns(3)

    with col1:
        total_orders = all_df['order_id'].nunique()
        st.metric("Total Order", f"{total_orders:,}")
 
    with col2:
        mean_rating = all_df['review_score'].mean() 
        st.metric("Rata-rata Rating", f"{mean_rating:.2f} ⭐️")

    with col3:
        total_products = all_df['product_id'].nunique()
        st.metric("Total Produk", f"{total_products:,}")

    # menampilkan informasi tentang performa penjualan dari setiap produk
    st.subheader("🌟 Kategori Produk berdasarkan Rating")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(40, 17))

    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    ## menampilkan kategori produk dengan review tertinggi
    sns.barplot(
        x="review_score",
        y="product_category_name_english",
        hue="product_category_name_english",
        data=avg_rev_score.head(5),
        palette=colors,
        legend=False,
        ax=ax[0]
    )
    ax[0].set_title("Kategori Produk dengan Rating Tertinggi", loc="center", fontsize=38)
    ax[0].set_xlabel(None)
    ax[0].set_ylabel(None)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelsize=30)

    ## menampilkan kategori produk dengan review terendah
    sns.barplot(
        x="review_score",
        y="product_category_name_english",
        hue="product_category_name_english",
        data=avg_rev_score.sort_values(by="review_score", ascending=True).head(5),
        palette=colors,
        legend=False,
        ax=ax[1]
    )
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Kategori Produk dengan Rating Terendah", loc="center", fontsize=38)
    ax[1].set_xlabel(None)
    ax[1].set_ylabel(None)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelsize=30)

    st.pyplot(fig)

    # membuat bar chart terkait distribusi skor review
    st.subheader("😊 Tingkat Kepuasan Pelanggan")

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(30, 12))

    review_counts.plot(kind="bar", color=colors)
    plt.title("Distribusi Rating Pelanggan", fontsize=25)
    plt.xlabel("Rating", fontsize=20)
    plt.xticks(rotation=0)
    plt.tick_params(axis='x', labelsize=20)
    plt.tick_params(axis='y', labelsize=20)
    st.pyplot(fig)

    # menampilkan informasi tentang performa penjualan dari setiap produk
    st.subheader("📦 Produk Paling Laku dan Sedikit Terjual")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 10))

    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    ## menampilkan kategori produk dengan penjualan paling banyak
    sns.barplot(
        x="total_sales",
        y="product_category_name_english",
        hue="product_category_name_english",
        data=sum_order_items_df.head(5),
        palette=colors,
        legend=False,
        ax=ax[0]
    )
    ax[0].set_title("Kategori Produk Terlaris", loc="center", fontsize=25)
    ax[0].set_xlabel(None)
    ax[0].set_ylabel(None)
    ax[0].tick_params(axis='y', labelsize=18)
    ax[0].tick_params(axis="x", labelsize=18)

    ## menampilkan kategori produk dengan penjualan paling sedikit
    sns.barplot(
        x="total_sales",
        y="product_category_name_english",
        hue="product_category_name_english",
        data=sum_order_items_df.sort_values(by="total_sales", ascending=True).head(5),
        palette=colors,
        legend=False,
        ax=ax[1]
    )
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Kategori Produk Kurang Laku", loc="center", fontsize=25)
    ax[1].set_xlabel(None)
    ax[1].set_ylabel(None)
    ax[1].tick_params(axis="y", labelsize=18)
    ax[1].tick_params(axis="x", labelsize=18)
    
    st.pyplot(fig)

    # menambahkan informasi mengenai Jumlah Pelanggan dan Seller Terbanyak 
    st.subheader("📍 Lokasi dengan Jumlah Pelanggan dan Seller Terbanyak")
    
    ## baris 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Kota dengan Pelanggan Terbanyak", value=cust_bycity.index[0], delta=f"{cust_bycity.iloc[0]} pelanggan")
     
    with col2: 
        st.metric("Kota dengan Seller Terbanyak", value=seller_bycity.index[0], delta=f"{seller_bycity.iloc[0]} seller")
    
    ## baris 2
    col3, col4 = st.columns(2)
    with col3:
        st.metric("State dengan Pelanggan Terbanyak", value=cust_bystate.index[0], delta=f"{cust_bystate.iloc[0]} pelanggan")
     
    with col4: 
        st.metric("State dengan Seller Terbanyak", value=seller_bystate.index[0], delta=f"{seller_bystate.iloc[0]} seller")
    
    # menampilkan informasi tentang persebaran pelanggan dan seller yang dimiliki
    st.subheader("🗺 Persebaran Pelanggan dan Seller")
    
    ## membaca file HTML
    with open("persebaran_cust_seller.html", "r", encoding="utf-8") as f:
        html_data = f.read()
    
    components.html(html_data, height=400, width=800)

else:
    st.warning("Silakan upload file terlebih dahulu.")

st.caption('Copyright (c) Bela Ismawati Nuraisa 2025')
