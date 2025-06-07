import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Interactive Media Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fungsi Pembantu ---

# Fungsi untuk membersihkan data
@st.cache_data
def clean_data(df):
    """
    Membersihkan data:
    - Mengubah 'Date' ke format datetime.
    - Mengisi 'Engagements' yang kosong dengan 0.
    """
    if 'Date' in df.columns:
        # Menangani berbagai format tanggal dan error parsing
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Hapus baris yang gagal diurai tanggalnya
        df.dropna(subset=['Date'], inplace=True)
    
    if 'Engagements' in df.columns:
        # Mengisi nilai kosong atau non-numerik dengan 0 dan mengkonversi ke integer
        df['Engagements'] = pd.to_numeric(df['Engagements'], errors='coerce').fillna(0).astype(int)
    
    return df

# Fungsi untuk membuat dan menampilkan grafik Plotly
def create_chart(chart_type, df, x=None, y=None, names=None, title="", color=None, sort_values=False, top_n=None):
    """
    Membuat grafik Plotly berdasarkan tipe yang diminta.
    """
    fig = None
    if chart_type == "pie":
        fig = px.pie(df, names=names, title=title, hole=0.4,
                     color_discrete_sequence=px.colors.pastel)
    elif chart_type == "line":
        if sort_values:
            df = df.sort_values(by=x)
        fig = px.line(df, x=x, y=y, title=title, markers=True,
                      color_discrete_sequence=px.colors.pastel)
    elif chart_type == "bar":
        if top_n:
            df = df.nlargest(top_n, y) # Ambil N teratas
        fig = px.bar(df, x=x, y=y, title=title,
                     color_discrete_sequence=px.colors.pastel)
    
    if fig:
        fig.update_layout(
            margin=dict(t=50, b=0, l=0, r=0),
            title_x=0.5,
            font=dict(family="Inter", size=12, color="#333"),
            hoverlabel=dict(font_size=12, font_family="Inter"),
            paper_bgcolor="#F0F8FF", # Alice Blue
            plot_bgcolor="rgba(0,0,0,0)" # Transparan
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- Judul Dashboard ---
st.markdown(
    """
    <style>
    .header-gradient {
        background: linear-gradient(to right, #B3E0FF, #8CD6FF);
        padding: 1rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 2rem;
    }
    .header-gradient h1 {
        color: #FFFFFF;
        font-size: 2.5rem;
        font-weight: bold;
        font-family: 'Inter', sans-serif;
    }
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 0.5rem;
        border-color: #BFDBFE;
    }
    .stMultiSelect div[data-baseweb="select"] {
        border-radius: 0.5rem;
        border-color: #BFDBFE;
    }
    .stDateInput div[data-baseweb="baseinput"] {
        border-radius: 0.5rem;
        border-color: #BFDBFE;
    }
    .stButton > button {
        background-color: #4A90E2; /* Blue-500 */
        color: white;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        background-color: #357ABD; /* Darker Blue-600 */
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    .chart-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        height: 100%;
        margin-bottom: 1.5rem; /* Consistent spacing */
    }
    .insights-box {
        background-color: #E0F2F7; /* Light blue pastel */
        padding: 1rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        color: #2A5280; /* Darker blue for text */
        margin-top: 1rem;
    }
    .insights-box ul {
        list-style-type: disc;
        margin-left: 1.25rem;
    }
    .insights-box li {
        margin-bottom: 0.25rem;
    }
    </style>
    <div class="header-gradient">
        <h1>Interactive Media Intelligence Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("---")

# --- Masukan Data ---
st.sidebar.header("Masukan Data")
uploaded_file = st.sidebar.file_uploader("Unggah File CSV", type=["csv"])

df = pd.DataFrame() # Inisialisasi DataFrame kosong

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File CSV berhasil diunggah!")
    
    # 2. Pembersihan Data
    df = clean_data(df.copy()) # Gunakan copy agar tidak mengubah DataFrame asli
    st.sidebar.success("Data berhasil dibersihkan!")
    st.dataframe(df.head(), use_container_width=True) # Tampilkan beberapa baris data yang telah dibersihkan
    
    # Kumpulkan nilai unik untuk filter
    all_platforms = ['Semua Platform'] + sorted(df['Platform'].unique().tolist()) if 'Platform' in df.columns else ['Semua Platform']
    all_media_types = ['Semua Tipe Media'] + sorted(df['MediaType'].unique().tolist()) if 'MediaType' in df.columns else ['Semua Tipe Media']
    all_locations = ['Semua Lokasi'] + sorted(df['Location'].unique().tolist()) if 'Location' in df.columns else ['Semua Lokasi']

    # --- Filter Data ---
    st.sidebar.write("---")
    st.sidebar.header("Filter Data")

    selected_platform = st.sidebar.selectbox("Platform", all_platforms)
    selected_sentiment = st.sidebar.selectbox("Sentimen", ["Semua Sentimen", "Positive", "Neutral", "Negative"])
    selected_media_type = st.sidebar.selectbox("Tipe Media", all_media_types)
    selected_location = st.sidebar.selectbox("Lokasi", all_locations)

    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Rentang Tanggal (Mulai)", 
                                    value=df['Date'].min() if not df.empty else None,
                                    min_value=df['Date'].min() if not df.empty else None,
                                    max_value=df['Date'].max() if not df.empty else None
                                    )
    with col2:
        end_date = st.date_input("Rentang Tanggal (Selesai)", 
                                  value=df['Date'].max() if not df.empty else None,
                                  min_value=df['Date'].min() if not df.empty else None,
                                  max_value=df['Date'].max() if not df.empty else None
                                  )

    # Terapkan Filter
    filtered_df = df.copy()

    if selected_platform != "Semua Platform":
        filtered_df = filtered_df[filtered_df['Platform'] == selected_platform]
    if selected_sentiment != "Semua Sentimen":
        filtered_df = filtered_df[filtered_df['Sentiment'] == selected_sentiment]
    if selected_media_type != "Semua Tipe Media":
        filtered_df = filtered_df[filtered_df['MediaType'] == selected_media_type]
    if selected_location != "Semua Lokasi":
        filtered_df = filtered_df[filtered_df['Location'] == selected_location]
    
    # Filter tanggal
    if start_date:
        filtered_df = filtered_df[filtered_df['Date'] >= pd.Timestamp(start_date)]
    if end_date:
        filtered_df = filtered_df[filtered_df['Date'] <= pd.Timestamp(end_date)]

    # --- Visualisasi Data & Insights ---
    st.write("---")
    st.header("Visualisasi Data & Insights")

    if filtered_df.empty:
        st.warning("Tidak ada data yang tersedia setelah menerapkan filter.")
    else:
        # Baris 1: Sentiment Breakdown & Platform Engagements
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.subheader("Sentiment Breakdown")
            sentiment_counts = filtered_df['Sentiment'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment', 'Count']
            create_chart("pie", sentiment_counts, names='Sentiment', title="Distribusi Sentimen")
            st.markdown(
                """
                <div class="insights-box">
                    <p class="font-bold">Insight:</p>
                    <ul>
                        <li>Mayoritas sentimen positif menunjukkan citra merek yang kuat.</li>
                        <li>Persentase sentimen netral yang signifikan mengindikasikan peluang untuk mengubah audiens yang ragu-ragu.</li>
                        <li>Perhatikan sentimen negatif; peningkatan tiba-tiba bisa menjadi sinyal masalah.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.subheader("Platform Engagements")
            platform_engagements = filtered_df.groupby('Platform')['Engagements'].sum().reset_index()
            create_chart("bar", platform_engagements, x='Platform', y='Engagements', title="Total Engagement per Platform")
            st.markdown(
                """
                <div class="insights-box">
                    <p class="font-bold">Insight:</p>
                    <ul>
                        <li>Platform dengan engagement tertinggi adalah saluran utama interaksi audiens Anda.</li>
                        <li>Platform dengan engagement rendah mungkin memerlukan evaluasi ulang strategi konten atau penargetan audiens.</li>
                        <li>Konten tertentu mungkin berkinerja lebih baik di platform spesifik, sesuaikan strategi Anda.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Baris 2: Engagement Trend over Time
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.subheader("Engagement Trend over Time")
        engagement_trend = filtered_df.groupby(pd.Grouper(key='Date', freq='D'))['Engagements'].sum().reset_index()
        engagement_trend.columns = ['Date', 'Total Engagements']
        create_chart("line", engagement_trend, x='Date', y='Total Engagements', title="Tren Engagement dari Waktu ke Waktu", sort_values=True)
        st.markdown(
            """
            <div class="insights-box">
                <p class="font-bold">Insight:</p>
                <ul>
                    <li>Lonjakan engagement setelah peluncuran kampanye menandakan keberhasilan.</li>
                    <li>Engagement cenderung memuncak dalam 24-48 jam pertama setelah publikasi konten.</li>
                    <li>Identifikasi tren musiman untuk merencanakan konten yang relevan.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)


        # Baris 3: Media Type Mix & Top 5 Locations
        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.subheader("Media Type Mix")
            media_type_counts = filtered_df['MediaType'].value_counts().reset_index()
            media_type_counts.columns = ['MediaType', 'Count']
            create_chart("pie", media_type_counts, names='MediaType', title="Proporsi Tipe Media")
            st.markdown(
                """
                <div class="insights-box">
                    <p class="font-bold">Insight:</p>
                    <ul>
                        <li>Tipe media dominan mencerminkan preferensi audiens Anda.</li>
                        <li>Jika artikel memiliki engagement tinggi tetapi proporsinya rendah, pertimbangkan untuk membuat lebih banyak.</li>
                        <li>Diversifikasi tipe media dapat membantu menjangkau audiens yang lebih luas.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.subheader("Top 5 Locations by Engagement")
            location_engagements = filtered_df.groupby('Location')['Engagements'].sum().reset_index()
            create_chart("bar", location_engagements, x='Location', y='Engagements', title="Top 5 Lokasi berdasarkan Engagement", top_n=5)
            st.markdown(
                """
                <div class="insights-box">
                    <p class="font-bold">Insight:</p>
                    <ul>
                        <li>Lokasi teratas adalah area dengan minat tinggi terhadap merek/topik Anda.</li>
                        <li>Data ini mendukung kampanye pemasaran atau konten yang dilokalisasi.</li>
                        <li>Area di luar 5 besar dengan engagement yang muncul bisa menjadi target ekspansi.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Silakan unggah file CSV Anda di sidebar untuk melihat visualisasi data.")
    st.write("Pastikan file CSV memiliki kolom: `Date`, `Platform`, `Sentiment`, `MediaType`, `Location`, `Engagements`.")

st.markdown("---")

# --- Fitur Ekspor Dashboard ---
st.header("Fitur Ekspor Dashboard")
st.write("""
Streamlit tidak memiliki fitur ekspor PDF bawaan secara langsung dari aplikasi.
Namun, Anda dapat menggunakan fungsi cetak browser (`Ctrl + P` atau `Cmd + P`)
dan menyimpannya sebagai PDF untuk mendapatkan salinan dashboard Anda.
""")

st.write("---")
