# -*- coding: utf-8 -*-
"""Halaman 4: Insight EDA & Pola Bisnis (2013–2017)."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from utils.data_loader import load_eda_tables
from utils.plotting import (
    BASE_LAYOUT,
    plot_dow_index,
    plot_earthquake_window,
    plot_monthly_trend,
    plot_oil_vs_sales,
    plot_pareto,
)
from utils.styles import PALETTE, fmt_id, render_page_header
from utils.tour import render_tour_banner


def render_eda(filters: dict) -> None:
    render_tour_banner()
    render_page_header(
        "Beranda / Insight EDA",
        "Insight Data & Pola Bisnis (2013–2017)",
        "Temuan utama dari analisis eksploratif seluruh dataset Corporación Favorita: pola musiman, efek gajian, hari libur, gempa 2016, harga minyak, dan Pareto kategori.",
    )

    eda = load_eda_tables()
    daily = eda["daily"]
    monthly = eda["monthly"]
    dow = eda["dow"]
    pareto = eda["pareto"]
    holiday = eda["holiday"]

    t1, t2, t3, t4, t5, t6 = st.tabs(
        ["📆 Pola Musiman", "💸 Hari Gajian", "🎉 Libur & Event", "🌋 Gempa 2016", "🛢️ Harga Minyak", "📦 Pareto Kategori"]
    )

    with t1:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            with st.container(border=True):
                st.markdown("**Rata-rata Penjualan per Hari dalam Seminggu**")
                st.caption("Indeks (Senin = 100). Batang pink menandai akhir pekan.")
                st.plotly_chart(plot_dow_index(dow, height=340), use_container_width=True)
        with c2:
            with st.container(border=True):
                st.markdown("**Tren Total Penjualan Bulanan 2013–2017**")
                st.caption("Juta unit per bulan · Bintang kuning menandai lonjakan rutin bulan Desember.")
                st.plotly_chart(plot_monthly_trend(monthly, height=340), use_container_width=True)

        i1, i2, i3, i4 = st.columns(4, gap="medium")
        cards = [
            ("📆", "Pola Mingguan Kuat", "Sabtu & Minggu ±20–30% lebih ramai dari hari kerja; Kamis cenderung paling landai.", PALETTE["primary"]),
            ("🎄", "Puncak Desember", "Setiap Desember terjadi lonjakan musiman belanja akhir tahun.", PALETTE["violet"]),
            ("💸", "Efek Gajian", "Tanggal 15 & akhir bulan memicu kenaikan belanja kebutuhan pokok.", PALETTE["amber"]),
            ("📈", "Autokorelasi Tinggi", "Rata-rata 7 & 14 hari terakhir menyumbang >83% gain pada model LightGBM.", PALETTE["cyan"]),
        ]
        for col_w, (ico, ttl, desc, clr) in zip([i1, i2, i3, i4], cards):
            with col_w:
                st.markdown(
                    f"""
                    <div class="fc-card" style="min-height:145px;">
                        <div style="font-size:22px;margin-bottom:6px;">{ico}</div>
                        <div class="fc-card-title" style="color:{clr};">{ttl}</div>
                        <div style="font-size:12px;color:#94A3B8;line-height:1.45;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with t2:
        with st.container(border=True):
            st.markdown("**Perbandingan Penjualan: Tanggal Gajian (15 & Akhir Bulan) vs Hari Biasa**")
            st.caption("Gaji sektor publik di Ekuador dibayarkan setiap tanggal 15 dan akhir bulan.")
            pay_df = daily[daily["sales"] > 0].copy()
            pay_df["Status Hari"] = pay_df["is_payday"].map({True: "Tanggal Gajian (15 / Akhir Bulan)", False: "Hari Biasa"})
            pay_agg = pay_df.groupby("Status Hari", as_index=False)["sales"].agg(
                Rata_rata="mean", Median="median", Jumlah_Hari="count"
            )
            c_l, c_r = st.columns([1.3, 1.0], gap="medium")
            with c_l:
                fig_p = px.bar(
                    pay_agg,
                    x="Status Hari",
                    y="Rata_rata",
                    color="Status Hari",
                    color_discrete_sequence=[PALETTE["primary"], PALETTE["amber"]],
                    text=pay_agg["Rata_rata"].map(lambda v: fmt_id(v / 1e3, 0) + " rb"),
                )
                fig_p.update_layout(**BASE_LAYOUT, showlegend=False, height=320, yaxis_title="Rata-rata unit / hari")
                st.plotly_chart(fig_p, use_container_width=True)
            with c_r:
                st.dataframe(pay_agg.round(0), use_container_width=True, hide_index=True)
                st.info(
                    "Fitur `is_payday`, `is_month_start`, dan `is_month_end` ditambahkan ke model untuk menangkap lonjakan ini secara otomatis."
                )

    with t3:
        with st.container(border=True):
            st.markdown("**Rasio Penjualan pada Hari Libur & Event terhadap Tren 29 Hari Sekitarnya**")
            st.caption("Rasio > 1,00 berarti penjualan hari tersebut lebih tinggi dari tren bulan sekitarnya. Baris `transferred=True` sudah dibersihkan.")
            c_l, c_r = st.columns([1.4, 1.0], gap="medium")
            with c_l:
                fig_h = px.bar(
                    holiday.sort_values("median_rasio", ascending=False),
                    x="kelompok_hari",
                    y="median_rasio",
                    color="kelompok_hari",
                    text=holiday.sort_values("median_rasio", ascending=False)["median_rasio"].map(lambda x: f"{x:.3f}×"),
                )
                fig_h.add_hline(y=1.0, line_dash="dash", line_color="#94A3B8")
                fig_h.update_layout(**BASE_LAYOUT, showlegend=False, height=330, yaxis_title="Median Rasio terhadap Tren")
                st.plotly_chart(fig_h, use_container_width=True)
            with c_r:
                st.dataframe(
                    holiday.rename(
                        columns={
                            "kelompok_hari": "Kelompok Hari",
                            "jumlah_hari": "Jumlah Hari",
                            "median_rasio": "Median Rasio",
                            "mean_rasio": "Rata-rata Rasio",
                        }
                    ).round(3),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption("Event nasional (seperti Hari Ibu / Black Friday) & libur yang dipindah (`Transfer`) menunjukkan perilaku berbeda dari hari biasa.")

    with t4:
        with st.container(border=True):
            st.markdown("**🌋 Dampak Gempa Ekuador M7,8 (16 April 2016)**")
            st.caption("Lonjakan tajam pembelian kebutuhan pokok & barang bantuan pasca gempa selama ±30 hari.")
            st.plotly_chart(plot_earthquake_window(daily, height=350), use_container_width=True)
            st.warning(
                "**Keputusan Pemodelan:** Data ekstrem saat gempa **tidak dibuang**, melainkan ditandai dengan fitur biner `pasca_gempa` (30 hari setelah 16 April 2016) "
                "agar model tidak salah menganggap lonjakan satu kali sebagai tren permanen."
            )

    with t5:
        with st.container(border=True):
            st.markdown("**🛢️ Pergerakan Harga Minyak Mentah WTI vs Total Penjualan Ritel**")
            st.caption("Ekonomi Ekuador bergantung pada minyak, namun penurunan tajam harga minyak 2014–2016 tidak menurunkan penjualan ritel secara langsung.")
            st.plotly_chart(plot_oil_vs_sales(monthly, height=350), use_container_width=True)
            st.info("Harga minyak dimasukkan dalam bentuk fitur lag (`oil_lag16` dan `oil_ma7_lag16`) agar bebas dari kebocoran masa depan.")

    with t6:
        with st.container(border=True):
            st.markdown("**📦 Distribusi Pareto Kategori Produk (33 Kategori)**")
            st.caption("Sedikit kategori utama (terutama GROCERY I & BEVERAGES) mendominasi total volume penjualan.")
            top_n = st.slider("Tampilkan Top-N Kategori", min_value=5, max_value=33, value=12, step=1)
            st.plotly_chart(plot_pareto(pareto, top_n=top_n, height=360), use_container_width=True)

            with st.expander("Lihat tabel lengkap 33 kategori & rasio efek promosi"):
                tbl_p = pareto[["family", "total_sales", "share_pct", "cum_share_pct", "zero_share", "promo_lift_ratio"]].copy()
                tbl_p.columns = ["Kategori", "Total Sales", "Pangsa (%)", "Kumulatif (%)", "Proporsi Nol", "Rasio Promo/Non-Promo"]
                st.dataframe(tbl_p.round(3), use_container_width=True, hide_index=True)
