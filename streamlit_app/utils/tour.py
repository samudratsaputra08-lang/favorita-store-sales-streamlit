# -*- coding: utf-8 -*-
"""Interactive Onboarding Welcome & 5-Step Guided Coach-Mark Tour."""
from __future__ import annotations

import streamlit as st

TOUR_STEPS = [
    {
        "title": "👋 Selamat Datang di Tur Interaktif",
        "desc": "Aplikasi ini mengubah model LightGBM (RMSLE 0,4045) dari Mini Project Kelompok 7 menjadi dashboard interaktif untuk perencanaan stok dan promo.",
        "page": "home",
    },
    {
        "title": "🎛️ Atur Filter Global di Sidebar",
        "desc": "Gunakan filter Periode, Tipe Toko (A–E), Provinsi, dan Klaster di panel kiri. Semua ringkasan dan grafik di Beranda otomatis menyesuaikan pilihan Anda.",
        "page": "home",
    },
    {
        "title": "📈 Telusuri Forecast Toko & Produk",
        "desc": "Di halaman Forecast Explorer, pilih nomor toko & kategori produk tertentu untuk melihat grafik histori 30/60/90 hari, forecast 16 hari, pita interval, serta tombol unduh CSV/Excel.",
        "page": "explorer",
    },
    {
        "title": "🧪 Uji Skenario Promo & Safety Stock",
        "desc": "Di halaman Simulasi What-If, geser jumlah promo dan lead time pemasok untuk menjalankan inferensi model LightGBM secara real-time dan menghitung Safety Stock (SS = Z × σ × √L).",
        "page": "simulator",
    },
    {
        "title": "📘 Eksplorasi Data, Model & Panduan",
        "desc": "Cek pola musiman di Insight EDA, leaderboard 6 model di Performa Model, atau kunjungi Panduan & Bantuan kapan saja untuk Glosarium dan FAQ.",
        "page": "guide",
    },
]


def init_tour_state() -> None:
    if "show_onboarding" not in st.session_state:
        st.session_state["show_onboarding"] = False
    if "tour_active" not in st.session_state:
        st.session_state["tour_active"] = False
    if "tour_step" not in st.session_state:
        st.session_state["tour_step"] = 0


def render_onboarding_screen() -> bool:
    """Tampilkan layar Onboarding penuh jika pengguna memilih membukanya."""
    if not st.session_state.get("show_onboarding", False):
        return False

    st.markdown(
        """
        <div class="fc-hero" style="padding: 36px 36px; text-align: center;">
            <div style="font-size: 40px; margin-bottom: 10px;">📈</div>
            <h2 style="font-size: 32px !important; margin-bottom: 10px !important;">Selamat Datang di Favorita Forecast</h2>
            <p style="margin: 0 auto; max-width: 680px; font-size: 15px;">
                Ramal penjualan harian <strong>54 toko × 33 kategori</strong> untuk <strong>16 hari ke depan</strong>,
                simulasikan efek promosi, dan hitung <em>safety stock</em> secara otomatis berbasis model
                <strong>LightGBM (tuned)</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            """
            <div class="fc-card">
                <div style="font-size:26px;margin-bottom:8px;">📈</div>
                <div class="fc-card-title">Forecast Akurat</div>
                <div style="font-size:13px;color:#94A3B8;line-height:1.5;">
                    LightGBM (tuned) mencapai WAPE 13,6% & RMSLE 0,4045 — 26,9% lebih rendah dibanding baseline terbaik.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="fc-card">
                <div style="font-size:26px;margin-bottom:8px;">🧪</div>
                <div class="fc-card-title">Simulasi What-If</div>
                <div style="font-size:13px;color:#94A3B8;line-height:1.5;">
                    Uji perubahan jumlah item promosi & lead time pemasok dengan inferensi langsung dari model ML.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="fc-card">
                <div style="font-size:26px;margin-bottom:8px;">📘</div>
                <div class="fc-card-title">Panduan & Transparansi</div>
                <div style="font-size:13px;color:#94A3B8;line-height:1.5;">
                    Dilengkapi tur interaktif 5 langkah, FAQ, glosarium metrik, serta analisis EDA & feature importance.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    b1, b2, b3, b4 = st.columns([1.2, 1.3, 1.3, 1.2])
    with b2:
        if st.button("🚀 Mulai Tur (5 Langkah)", type="primary", use_container_width=True):
            st.session_state["show_onboarding"] = False
            st.session_state["tour_active"] = True
            st.session_state["tour_step"] = 0
            st.session_state["nav_target"] = "home"
            st.rerun()
    with b3:
        if st.button("Langsung ke Beranda →", use_container_width=True):
            st.session_state["show_onboarding"] = False
            st.session_state["tour_active"] = False
            st.rerun()

    return True


def render_tour_banner() -> None:
    """Render kotak coach-mark interaktif di bagian atas halaman saat tur aktif."""
    if not st.session_state.get("tour_active", False):
        return

    step_idx = int(st.session_state.get("tour_step", 0))
    step = TOUR_STEPS[step_idx]
    total = len(TOUR_STEPS)

    st.markdown(
        f"""
        <div class="fc-tour-box">
            <span class="fc-tour-step">TUR INTERAKTIF · LANGKAH {step_idx + 1} DARI {total}</span>
            <div class="fc-tour-title">{step['title']}</div>
            <div class="fc-tour-desc">{step['desc']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, _ = st.columns([1, 1, 1.1, 2.5])
    with c1:
        if st.button("✕ Lewati Tur", key="tour_skip", use_container_width=True):
            st.session_state["tour_active"] = False
            st.rerun()
    with c2:
        if st.button("← Kembali", key="tour_prev", disabled=(step_idx == 0), use_container_width=True):
            new_idx = max(0, step_idx - 1)
            st.session_state["tour_step"] = new_idx
            st.session_state["nav_target"] = TOUR_STEPS[new_idx]["page"]
            st.rerun()
    with c3:
        next_label = "Selesai ✓" if step_idx == total - 1 else "Lanjut →"
        if st.button(next_label, key="tour_next", type="primary", use_container_width=True):
            if step_idx == total - 1:
                st.session_state["tour_active"] = False
            else:
                new_idx = step_idx + 1
                st.session_state["tour_step"] = new_idx
                st.session_state["nav_target"] = TOUR_STEPS[new_idx]["page"]
            st.rerun()
