# 📊 Dasbor Analisis Penjualan Superstore

Dasbor interaktif ini dibangun menggunakan Streamlit dan Plotly untuk menganalisis data penjualan Superstore. Tujuannya adalah untuk memberikan wawasan yang mudah dipahami tentang kinerja penjualan, profitabilitas produk, segmentasi pelanggan, dampak diskon, dan tren dari waktu ke waktu. Dasbor ini dirancang untuk mendukung pengambilan keputusan strategis dan analitis.

**Proyek ini merupakan bagian dari tugas Ujian Akhir Semester (UAS) untuk mata kuliah Visualisasi Data.**

## ✨ Fitur Utama

Dasbor ini terbagi menjadi beberapa bagian untuk analisis yang komprehensif:

1.  **Gambaran Umum Eksekutif**:
    * Metrik Kinerja Utama (KPI) seperti Total Penjualan, Total Keuntungan, Margin Keuntungan, dan Total Pesanan.
    * Dilengkapi dengan indikator delta (perubahan) dibandingkan periode sebelumnya untuk konteks yang lebih kaya.
    * Visualisasi tren penjualan dan keuntungan tahunan dan bulanan.
    * Analisis penjualan dan keuntungan berdasarkan segmen pelanggan.

2.  **Kategori & Produk**:
    * Treemap interaktif yang menunjukkan penjualan dan keuntungan secara hierarkis berdasarkan Kategori dan Sub-Kategori.
    * Grafik batang horizontal untuk 10 Produk Paling Menguntungkan dan 10 Produk Paling Merugi.
    * Heatmap profitabilitas untuk mengidentifikasi kinerja sub-kategori di setiap kategori.

3.  **Segmentasi Pelanggan**:
    * Diagram lingkaran (pie chart) yang menunjukkan rata-rata keuntungan per segmen pelanggan.
    * Grafik batang yang menampilkan total penjualan per segmen pelanggan.
    * Daftar 10 Pelanggan Paling Menguntungkan.

4.  **Analisis Diskon**:
    * Scatter plot yang menganalisis hubungan antara Margin Keuntungan dan Diskon, dilengkapi dengan garis tren.
    * Histogram distribusi tingkat diskon.
    * Grafik batang yang menunjukkan rata-rata Penjualan dan Keuntungan per tingkat diskon yang berbeda (Tanpa Diskon, Rendah, Sedang, Tinggi).

5.  **Deret Waktu**:
    * Visualisasi tren bulanan dan tahunan untuk Penjualan, Keuntungan, atau Margin Keuntungan (dapat dipilih pengguna).

6.  **Peta Profit Geografis**:
    * Peta choropleth yang menampilkan distribusi total keuntungan per Negara Bagian di Amerika Serikat.

## 🚀 Cara Menjalankan Aplikasi

Untuk menjalankan dasbor ini secara lokal di mesin Anda, ikuti langkah-langkah berikut:

1.  **Kloning Repositori (jika ini ada di GitHub):**
    ```bash
    git clone [https://github.com/your-username/your-streamlit-app.git](https://github.com/your-username/your-streamlit-app.git)
    cd your-streamlit-app
    ```
    *(Ganti `your-username/your-streamlit-app` dengan detail repositori Anda.)*

2.  **Buat dan Aktifkan Lingkungan Virtual (Direkomendasikan):**
    ```bash
    python -m venv venv
    # Di Windows:
    .\venv\Scripts\activate
    # Di macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instal Dependensi:**
    Pastikan Anda memiliki file `requirements.txt` di direktori proyek Anda. Kemudian instal dependensinya:
    ```bash
    pip install -r requirements.txt
    ```
    *Jika Anda belum memiliki `requirements.txt`, Anda dapat membuatnya setelah menginstal paket yang diperlukan secara manual:*
    ```bash
    pip install streamlit pandas plotly
    pip freeze > requirements.txt
    ```

4.  **Jalankan Aplikasi Streamlit:**
    ```bash
    streamlit run app.py
    ```

Setelah menjalankan perintah di atas, dasbor akan terbuka secara otomatis di browser web default Anda.

## 📂 Struktur Proyek