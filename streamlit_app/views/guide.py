# -*- coding: utf-8 -*-
"""Halaman 6: Panduan & Bantuan (Quick Start, Glosarium, FAQ, Tim)."""
from __future__ import annotations

import streamlit as st

from utils.styles import PALETTE, render_page_header
from utils.tour import render_tour_banner

GLOSARIUM = [
    ("RMSLE", "Root Mean Squared Logarithmic Error — mengukur selisih relatif pada skala logaritma. Metrik utama (makin kecil makin baik).", PALETTE["primary"]),
    ("WAPE", "Weighted Absolute Percentage Error — total error absolut dibagi total penjualan. Aman saat ada sales = 0.", PALETTE["cyan"]),
    ("MAE", "Mean Absolute Error — rata-rata selisih absolut dalam satuan unit asli produk per toko-kategori-hari.", PALETTE["green"]),
    ("R²", "Koefisien determinasi — proporsi variasi penjualan yang berhasil dijelaskan oleh model (mendekati 1 = makin baik).", PALETTE["amber"]),
    ("Safety stock", "Stok cadangan (SS = Z × σ × √L) untuk mengantisipasi lonjakan permintaan tak terduga selama lead time.", PALETTE["pink"]),
    ("Lag / Rolling", "Penjualan masa lalu (≥16 hari sebelumnya agar bebas bocoran masa depan) dan rata-rata bergulir 7/14/28 hari.", PALETTE["violet"]),
]

FAQS = [
    (
        "Mengapa horizon forecast 16 hari (16–31 Agustus 2017)?",
        "Mengikuti periode data uji kompetisi Kaggle Store Sales (16–31 Agustus 2017). Semua fitur lag historis digeser minimal 16 hari agar model benar-benar mensimulasikan kondisi meramal masa depan tanpa kebocoran data.",
    ),
    (
        "Bagaimana cara mengunduh forecast untuk toko tertentu?",
        "Buka halaman **Forecast Explorer**, pilih nomor Toko dan Kategori Produk, lalu klik tombol **Unduh Forecast (CSV)** atau **Unduh Forecast (Excel .xlsx)** di panel kanan bawah.",
    ),
    (
        "Mengapa kategori seperti SCHOOL AND OFFICE SUPPLIES memiliki error tinggi?",
        "Kategori tersebut bersifat sporadis (74% hari bernilai nol) dan mengalami lonjakan musiman sangat tajam di awal tahun ajaran. Karena sulit diprediksi stabil, tambahkan buffer stok ±40% pada Simulasi What-If.",
    ),
    (
        "Apakah hasil Simulasi What-If benar-benar dihitung oleh model LightGBM?",
        "Ya. Ketika Anda menggeser slider promosi atau mengubah toggle hari gajian/libur di halaman **Simulasi What-If**, aplikasi memanggil model `LightGBM (tuned)` secara langsung untuk menghasilkan prediksi skenario.",
    ),
    (
        "Bagaimana cara memperbarui data atau melatih ulang model?",
        "Jalankan ulang skrip `python scripts/export_artifacts.py` dengan dataset terbaru di folder sumber. Seluruh artefak di folder `artifacts/` akan diperbarui tanpa perlu mengubah kode UI Streamlit.",
    ),
    (
        "Bisakah saya melihat ringkasan semua toko sekaligus?",
        "Ya, pada halaman **Beranda**, klik tombol **Unduh Ringkasan Forecast per Toko (CSV)** tepat di bawah tabel Top 5 Toko untuk mendapatkan proyeksi seluruh 54 toko.",
    ),
]

TIM_KELOMPOK_7 = [
    ("ST", "Samudra Tsalasa Putra", "Business Understanding, Pemilihan Model & Integrasi Akhir", PALETTE["primary"]),
    ("DA", "Dwi Aura Ningrum", "Data Understanding (EDA) & Preprocessing Split Waktu", PALETTE["pink"]),
    ("AR", "Anavalis Ridho Abdee Nugroho", "Pemilihan Algoritma, Ridge, LightGBM & Tuning", PALETTE["cyan"]),
    ("HN", "Hany Nadya Fairuz", "Baseline, Random Forest, Cross-Validation & Interpretasi", PALETTE["green"]),
    ("EL", "Eka Lidya Rahmadini", "Setup Data Loading & Feature Engineering", PALETTE["amber"]),
    ("SK", "Selsa Trikartika", "Forecast 15 Hari, Submission & Aplikasi Streamlit", PALETTE["violet"]),
]


def render_guide(filters: dict) -> None:
    render_tour_banner()

    top_l, top_r = st.columns([3.5, 1.2])
    with top_l:
        render_page_header(
            "Beranda / Panduan & Bantuan",
            "Panduan & Bantuan",
            "Semua yang perlu Anda ketahui untuk menggunakan aplikasi: mulai cepat 5 langkah, cara membaca grafik, glosarium metrik, dan FAQ.",
        )
    with top_r:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("🎯 Ulangi Tur Interaktif", type="primary", use_container_width=True):
            st.session_state["tour_active"] = True
            st.session_state["tour_step"] = 0
            st.session_state["nav_target"] = "home"
            st.rerun()

    query = st.text_input("🔍 Cari panduan, istilah metrik, atau pertanyaan…", placeholder="contoh: RMSLE, CSV, safety stock, promo").strip().lower()

    st.markdown("### 🚀 Mulai Cepat — 5 Langkah")
    q_cols = st.columns(5, gap="small")
    q_steps = [
        ("1", "Atur Filter", "Pilih periode, tipe toko (A–E), provinsi & klaster di sidebar.", PALETTE["primary"]),
        ("2", "Baca Beranda", "Pahami KPI nasional, tren 90 hari, dan insight otomatis.", PALETTE["sky"]),
        ("3", "Pilih Toko", "Buka Forecast Explorer → pilih toko & kategori produk.", PALETTE["cyan"]),
        ("4", "Simulasikan", "Uji skenario promo & hitung Safety Stock di What-If.", PALETTE["pink"]),
        ("5", "Unduh Data", "Ekspor tabel forecast ke CSV atau Excel untuk tim gudang.", PALETTE["green"]),
    ]
    for col_w, (num, ttl, desc, clr) in zip(q_cols, q_steps):
        with col_w:
            st.markdown(
                f"""
                <div class="fc-qstep" style="border-top: 3px solid {clr};">
                    <div class="fc-qnum" style="background:{clr};">{num}</div>
                    <div style="font-size:14px;font-weight:700;color:#F1F5F9;margin-bottom:4px;">{ttl}</div>
                    <div style="font-size:12px;color:#94A3B8;line-height:1.45;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # Cara Membaca Grafik Forecast
    with st.container(border=True):
        st.markdown("**📈 Cara Membaca Grafik Forecast**")
        g1, g2, g3, g4 = st.columns(4, gap="medium")
        g1.markdown("**1. Bandingkan Level**\n\nPastikan proyeksi forecast sejalan dengan rata-rata histori 2–4 minggu terakhir.")
        g2.markdown("**2. Perhatikan Pola**\n\nPuncak rutin berulang setiap Sabtu–Minggu serta tanggal gajian (15 & akhir bulan).")
        g3.markdown("**3. Gunakan Pita Interval**\n\nGunakan batas atas pita interval sebagai patokan stok untuk produk fast-moving.")
        g4.markdown("**4. Cek Kategori Sulit**\n\nKategori dengan banyak hari nol (mis. School & Office) memerlukan penyangga stok ekstra.")

    c_gl, c_fq = st.columns([1.0, 1.15], gap="medium")

    with c_gl:
        with st.container(border=True):
            st.markdown("**📖 Glosarium Metrik & Istilah**")
            filtered_gl = [g for g in GLOSARIUM if not query or query in g[0].lower() or query in g[1].lower()]
            if not filtered_gl:
                st.caption("Tidak ada istilah yang cocok dengan kata kunci pencarian.")
            for term, desc, clr in filtered_gl:
                st.markdown(
                    f"""
                    <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid #25314D;">
                        <span class="fc-badge" style="background:{clr}24;color:{clr};min-width:96px;text-align:center;">{term}</span>
                        <div style="font-size:12px;color:#CBD5E1;line-height:1.5;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with c_fq:
        with st.container(border=True):
            st.markdown("**❓ Pertanyaan yang Sering Diajukan (FAQ)**")
            filtered_faq = [f for f in FAQS if not query or query in f[0].lower() or query in f[1].lower()]
            if not filtered_faq:
                st.caption("Tidak ada FAQ yang cocok dengan kata kunci pencarian.")
            for idx, (q, a) in enumerate(filtered_faq):
                with st.expander(q, expanded=(idx == 0 and not query)):
                    st.write(a)

    # Tim Pengembang
    with st.container(border=True):
        st.markdown("**👥 Tim Pengembang · Kelompok 7 (Celerates Independent Study)**")
        t_cols = st.columns(3, gap="medium")
        for i, (init, name, role, clr) in enumerate(TIM_KELOMPOK_7):
            with t_cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;gap:12px;padding:10px 12px;background:#0D1426;border:1px solid #25314D;border-radius:12px;margin-bottom:10px;">
                        <div style="width:36px;height:36px;border-radius:999px;background:{clr}33;color:{clr};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;flex-shrink:0;">{init}</div>
                        <div>
                            <div style="font-size:13px;font-weight:700;color:#F1F5F9;">{name}</div>
                            <div style="font-size:11px;color:#64748B;">{role}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
