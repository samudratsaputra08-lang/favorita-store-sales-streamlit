# 📈 Favorita Store Sales Forecasting App

Aplikasi web **Streamlit** berbasis *Dark Analytics UI* untuk meramalkan penjualan harian **54 toko × 33 kategori produk** jaringan supermarket **Corporación Favorita (Ekuador)** pada horizon **16 hari ke depan** (16–31 Agustus 2017).

Proyek ini merupakan implementasi dari **Mini Project Data Science & Generative AI — Kelompok 7 (Celerates Independent Study)**.

---

## ✨ Fitur Utama

1. **🏠 Beranda (Executive Dashboard)**
   - Kartu KPI nasional (Total Forecast, Rata-rata Harian, Akurasi WAPE/RMSLE, Cakupan Seri).
   - Grafik tren penjualan historis (30/60/90 hari) vs forecast 16 hari.
   - Top 5 Kategori Produk & Top 5 Toko + tombol unduh ringkasan CSV.
   - Panel *Insight Otomatis* (hari gajian, akhir pekan, kategori berisiko).
2. **📈 Forecast Explorer**
   - Eksplorasi mendalam per toko (1–54) dan kategori produk (33 `family`).
   - Pita interval perkiraan wajar & penanda hari gajian/akhir pekan.
   - Tabel harian, perbandingan pola mingguan, perbandingan antar toko, serta ekspor **CSV & Excel (`.xlsx`)**.
3. **🧪 Simulasi What-If & Safety Stock**
   - **Inferensi real-time model LightGBM (tuned)** ketika slider promosi atau toggle gajian/libur diubah.
   - Kalkulator otomatis **Safety Stock** ($SS = Z \times \sigma \times \sqrt{L}$) dan **Reorder Point**.
   - Tabel perbandingan skenario tersimpan.
4. **📊 Insight EDA (2013–2017)**
   - Pola mingguan, tren bulanan, efek tanggal gajian (15 & akhir bulan), dampak libur & event, lonjakan gempa Ekuador 16 April 2016, korelasi harga minyak WTI, dan analisis Pareto 33 kategori.
5. **⚙️ Performa & Transparansi Model**
   - Leaderboard 6 model (Seasonal Naive, Rata-rata 28 hari, Ridge, Random Forest, LightGBM, LightGBM Tuned).
   - Top 10 *Feature Importance* (gain) & kontribusi per kelompok fitur.
   - Kategori tersulit vs termudah diprediksi, scatter Aktual vs Prediksi, dan cek *overfitting*.
6. **📘 Panduan & Tur Interaktif**
   - Layar *Onboarding* + Tur Interaktif 5 langkah, pencarian panduan, Glosarium Metrik, dan FAQ.

---

## 🛠️ Struktur Direktori

```text
mini-project/
├── MiniProject_StoreSalesRegression_Kelompok7.ipynb
├── artifacts/                  # Data terkompresi (.csv.gz), metrik (.json) & model (.joblib)
├── scripts/
│   └── export_artifacts.py     # Pipeline ekstraksi dari dataset mentah ke artifacts/
├── streamlit_app/
│   ├── app.py                  # Entrypoint & navigasi
│   ├── .streamlit/config.toml  # Tema Dark Analytics
│   ├── utils/                  # Styles, data_loader, plotting, tour
│   └── views/                  # 6 halaman aplikasi
├── design/                     # Desain UI/UX FigCraft (build_ui.py)
├── Dockerfile.vercel           # Konfigurasi container untuk Vercel
├── vercel.json                 # Konfigurasi Fluid Compute Vercel
└── requirements.txt
```

---

## 🚀 Menjalankan Secara Lokal

```bash
# 1. Instal dependensi
pip install -r requirements.txt

# 2. (Opsional) Ekstrak ulang artefak jika mengubah data mentah
python scripts/export_artifacts.py

# 3. Jalankan aplikasi Streamlit
streamlit run streamlit_app/app.py
```

---

## 👥 Tim Pengembang — Kelompok 7
- **Samudra Tsalasa Putra**
- **Dwi Aura Ningrum**
- **Anavalis Ridho Abdee Nugroho**
- **Hany Nadya Fairuz**
- **Eka Lidya Rahmadini**
- **Selsa Trikartika**
