# -*- coding: utf-8 -*-
"""Halaman 1: Beranda (Executive Dashboard)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import load_forecast, load_history, load_model_artifacts, load_stores
from utils.plotting import plot_horizontal_bars, plot_national_trend
from utils.styles import PALETTE, fmt_id, render_kpi_card, render_page_header
from utils.tour import render_tour_banner


def render_home(filters: dict) -> None:
    render_tour_banner()

    top_l, top_r = st.columns([3.5, 1.3])
    with top_l:
        render_page_header(
            "Beranda",
            "Ringkasan Eksekutif",
            "Gambaran penjualan nasional dan proyeksi 16 hari ke depan (16–31 Agustus 2017) untuk seluruh toko Favorita.",
        )
    with top_r:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🎯 Tur", use_container_width=True, help="Mulai tur interaktif 5 langkah"):
                st.session_state["tour_active"] = True
                st.session_state["tour_step"] = 0
                st.rerun()
        with b2:
            if st.button("👋 Intro", use_container_width=True, help="Buka layar sambutan"):
                st.session_state["show_onboarding"] = True
                st.rerun()

    fc_all = load_forecast()
    hs_all = load_history()
    stores_df = load_stores()
    meta = load_model_artifacts()["metrics"]

    store_ids = filters["store_ids"]
    fc = fc_all[
        fc_all["store_nbr"].isin(store_ids)
        & (fc_all["date"] >= filters["date_start"])
        & (fc_all["date"] <= filters["date_end"])
    ].copy()
    hs = hs_all[hs_all["store_nbr"].isin(store_ids)].copy()

    if len(fc) == 0:
        st.warning("Belum ada data untuk kombinasi filter saat ini. Coba perluas filter Tipe Toko, Provinsi, atau Klaster di sidebar.")
        return

    n_days = max(int(fc["date"].nunique()), 1)
    fc_total = float(fc["sales_pred"].sum())
    daily_avg = fc_total / n_days

    hs_daily_all = hs.groupby("date", as_index=False)["sales"].sum().sort_values("date")
    prev_total = float(hs_daily_all.tail(n_days)["sales"].sum()) if len(hs_daily_all) else fc_total
    delta_pct = ((fc_total / prev_total) - 1.0) * 100.0 if prev_total > 0 else 0.0

    best_row = next((r for r in meta["leaderboard"] if r["model"] == meta["best_model"]), meta["leaderboard"][0])
    wape_pct = best_row["WAPE"] * 100.0
    rmsle_val = best_row["RMSLE"]

    # Hero Banner
    st.markdown(
        f"""
        <div class="fc-hero">
            <h2>Selamat datang kembali, Manajer 👋</h2>
            <p>
                Total penjualan <strong>{n_days} hari</strong> ke depan pada cakupan filter diperkirakan
                <strong>{fmt_id(fc_total / 1e6, 2)} juta unit</strong>
                ({'naik' if delta_pct >= 0 else 'turun'} {fmt_id(abs(delta_pct), 1)}% dibanding {n_days} hari terakhir).
                Puncak permintaan terjadi pada akhir pekan & tanggal gajian (31 Agustus).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("📈 Lihat Detail Forecast per Toko →", type="primary"):
        st.session_state["nav_target"] = "explorer"
        st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # 4 KPI Cards
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        sign = "▲" if delta_pct >= 0 else "▼"
        dcol = PALETTE["green"] if delta_pct >= 0 else PALETTE["red"]
        st.markdown(
            render_kpi_card(
                "💰",
                PALETTE["primary"],
                f"Total forecast {n_days} hari",
                f"{fmt_id(fc_total / 1e6, 2)} Jt",
                f"{sign} {fmt_id(abs(delta_pct), 1)}%",
                dcol,
                f"unit · vs {n_days} hari lalu",
            ),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            render_kpi_card(
                "📅",
                PALETTE["cyan"],
                "Rata-rata harian",
                f"{fmt_id(daily_avg / 1e3, 0)} rb",
                f"{len(store_ids)} toko aktif",
                PALETTE["cyan"],
                "unit per hari",
            ),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            render_kpi_card(
                "🎯",
                PALETTE["green"],
                "Akurasi model (WAPE)",
                f"{fmt_id(wape_pct, 1)}%",
                f"RMSLE {fmt_id(rmsle_val, 4)}",
                PALETTE["cyan"],
                "validasi 15 hari terakhir",
            ),
            unsafe_allow_html=True,
        )
    with k4:
        n_series = len(store_ids) * int(fc["family"].nunique())
        st.markdown(
            render_kpi_card(
                "🏪",
                PALETTE["amber"],
                "Cakupan deret waktu",
                f"{fmt_id(n_series)} seri",
                f"{len(store_ids)} toko · {fc['family'].nunique()} kategori",
                PALETTE["amber"],
                "kombinasi toko × kategori",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Row 2: National Trend + Top 5 Categories
    c_left, c_right = st.columns([1.85, 1.0], gap="medium")
    with c_left:
        with st.container(border=True):
            hdr_l, hdr_r = st.columns([2.2, 1.1])
            with hdr_l:
                st.markdown("**Tren Penjualan — Histori & Forecast**")
                st.caption("Total unit terjual per hari sesuai filter global. Arsir cyan = periode forecast.")
            with hdr_r:
                win_choice = st.segmented_control(
                    "Rentang histori",
                    options=["30H", "60H", "90H"],
                    default="90H",
                    label_visibility="collapsed",
                    key="home_hist_win",
                )
            days_back = int((win_choice or "90H").replace("H", ""))
            hs_plot = hs_daily_all.tail(days_back)
            fc_plot = fc.groupby("date", as_index=False)["sales_pred"].sum().sort_values("date")
            st.plotly_chart(plot_national_trend(hs_plot, fc_plot, height=340), use_container_width=True)

    with c_right:
        with st.container(border=True):
            st.markdown("**Top 5 Kategori Produk**")
            st.caption("Kontribusi total forecast (juta unit)")
            top_cats = (
                fc.groupby("family", as_index=False)["sales_pred"]
                .sum()
                .sort_values("sales_pred", ascending=False)
                .head(5)
            )
            cat_colors = [PALETTE["primary"], PALETTE["violet"], PALETTE["cyan"], PALETTE["green"], PALETTE["amber"]]
            st.plotly_chart(
                plot_horizontal_bars(
                    top_cats["family"].tolist(),
                    (top_cats["sales_pred"] / 1e6).tolist(),
                    colors=cat_colors[: len(top_cats)],
                    unit_suffix=" Jt",
                    height=295,
                ),
                use_container_width=True,
            )
            if st.button("Lihat semua 33 kategori di EDA →", key="home_to_eda", use_container_width=True):
                st.session_state["nav_target"] = "eda"
                st.rerun()

    # Row 3: Top 5 Stores Table + Automated Insights
    b_left, b_right = st.columns([1.4, 1.0], gap="medium")
    with b_left:
        with st.container(border=True):
            st.markdown("**🏆 Top 5 Toko (Total Forecast)**")
            st.caption("Berdasarkan proyeksi unit terjual pada periode terpilih")
            fc_store = fc.groupby("store_nbr", as_index=False)["sales_pred"].sum()
            hs_recent = (
                hs[hs["date"] > hs["date"].max() - pd.Timedelta(days=n_days)]
                .groupby("store_nbr", as_index=False)["sales"]
                .sum()
            )
            top_stores = (
                fc_store.merge(stores_df, on="store_nbr", how="left")
                .merge(hs_recent, on="store_nbr", how="left")
                .sort_values("sales_pred", ascending=False)
                .head(5)
            )
            top_stores["Perubahan (%)"] = ((top_stores["sales_pred"] / top_stores["sales"].replace(0, pd.NA)) - 1.0) * 100.0
            disp = pd.DataFrame(
                {
                    "Toko": top_stores["store_nbr"].map(lambda x: f"#{x}"),
                    "Kota": top_stores["city"],
                    "Tipe": top_stores["type"].map(lambda x: f"Tipe {x}"),
                    "Klaster": top_stores["cluster"],
                    "Forecast (unit)": top_stores["sales_pred"].map(lambda x: fmt_id(x, 0)),
                    "Δ vs periode lalu": top_stores["Perubahan (%)"].map(
                        lambda x: f"{'▲' if x >= 0 else '▼'} {fmt_id(abs(x), 1)}%" if pd.notna(x) else "—"
                    ),
                }
            )
            st.dataframe(disp, use_container_width=True, hide_index=True)

            # Download executive summary CSV
            all_store_summary = (
                fc_store.merge(stores_df, on="store_nbr", how="left")
                .sort_values("sales_pred", ascending=False)
            )
            st.download_button(
                "📥 Unduh Ringkasan Forecast per Toko (CSV)",
                data=all_store_summary.to_csv(index=False).encode("utf-8"),
                file_name="ringkasan_forecast_per_toko.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with b_right:
        with st.container(border=True):
            st.markdown("**✨ Insight Otomatis**")
            st.caption("Dirangkum dari hasil forecast & temuan EDA")
            insights = [
                (
                    "💸",
                    "Hari gajian 31 Agustus",
                    "Penjualan pada tanggal gajian sektor publik (15 & akhir bulan) rata-rata ±9% lebih tinggi. Pastikan stok GROCERY I & BEVERAGES aman.",
                    PALETTE["amber"],
                ),
                (
                    "📆",
                    "Lonjakan akhir pekan (Sab–Min)",
                    "Volume penjualan Sabtu–Minggu ±20% di atas hari kerja. Sesuaikan jadwal staf kasir & pengisian rak.",
                    PALETTE["violet"],
                ),
                (
                    "⚠️",
                    "Kategori volatil & sporadis",
                    "SCHOOL AND OFFICE SUPPLIES (74% hari nol) dan LINGERIE memiliki RMSLE tertinggi — tambahkan penyangga stok (buffer).",
                    PALETTE["red"],
                ),
            ]
            for ico, ttl, body, col in insights:
                st.markdown(
                    f"""
                    <div class="fc-insight" style="background:{col}15;border:1px solid {col}40;">
                        <div style="font-size:20px;line-height:1;">{ico}</div>
                        <div>
                            <div class="fc-insight-title" style="color:{col};">{ttl}</div>
                            <div class="fc-insight-body">{body}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
