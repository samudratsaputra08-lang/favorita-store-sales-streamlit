# -*- coding: utf-8 -*-
"""Halaman 2: Forecast Explorer (Detail per Toko & Kategori)."""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from utils.data_loader import load_family_stats, load_forecast, load_history, load_stores
from utils.plotting import plot_explorer_series
from utils.styles import PALETTE, fmt_id, render_kpi_card, render_page_header
from utils.tour import render_tour_banner

HARI_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def _to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Forecast_16_Hari")
    return buf.getvalue()


def render_explorer(filters: dict) -> None:
    render_tour_banner()
    render_page_header(
        "Beranda / Forecast Explorer",
        "Forecast Explorer",
        "Telusuri ramalan penjualan per toko dan kategori produk, lengkap dengan pita interval dan tabel harian yang dapat diunduh.",
    )

    stores_df = load_stores()
    fc_all = load_forecast()
    hs_all = load_history()
    fam_stats = load_family_stats()

    avail_stores = filters["store_ids"] or sorted(stores_df["store_nbr"].astype(int).tolist())
    store_meta_map = stores_df.set_index("store_nbr").to_dict("index")
    store_labels = {
        s: f"Toko {s} · {store_meta_map[s]['city']} · Tipe {store_meta_map[s]['type']}"
        for s in avail_stores
    }

    all_families = sorted(fc_all["family"].unique().tolist())
    default_store = 44 if 44 in avail_stores else avail_stores[0]
    default_fam_idx = all_families.index("GROCERY I") if "GROCERY I" in all_families else 0

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1.45, 1.3, 1.0, 0.85], gap="medium")
        with c1:
            sel_store = st.selectbox(
                "🏪 Pilih Toko",
                options=avail_stores,
                index=avail_stores.index(default_store),
                format_func=lambda s: store_labels[s],
                help="Daftar toko mengikuti filter Tipe/Provinsi/Klaster di sidebar.",
            )
        with c2:
            sel_fam = st.selectbox(
                "🛒 Kategori Produk",
                options=all_families,
                index=default_fam_idx,
            )
        with c3:
            hist_win = st.segmented_control(
                "Rentang histori",
                options=["30H", "60H", "90H"],
                default="60H",
            )
        with c4:
            st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
            show_interval = st.toggle("Pita interval", value=True)

    days_back = int((hist_win or "60H").replace("H", ""))

    fc = fc_all[
        (fc_all["store_nbr"] == sel_store)
        & (fc_all["family"] == sel_fam)
        & (fc_all["date"] >= filters["date_start"])
        & (fc_all["date"] <= filters["date_end"])
    ].sort_values("date")

    hs = (
        hs_all[(hs_all["store_nbr"] == sel_store) & (hs_all["family"] == sel_fam)]
        .sort_values("date")
        .tail(days_back)
    )

    if len(fc) == 0:
        st.info("Tidak ada baris forecast pada rentang tanggal yang dipilih.")
        return

    tot_fc = float(fc["sales_pred"].sum())
    avg_fc = tot_fc / len(fc)
    peak_row = fc.loc[fc["sales_pred"].idxmax()]
    peak_dt = peak_row["date"]
    peak_str = f"{HARI_ID[peak_dt.weekday()]}, {peak_dt.day} Agu"

    prev_same_len = hs.tail(len(fc))["sales"].sum()
    delta_pct = ((tot_fc / prev_same_len) - 1.0) * 100.0 if prev_same_len > 0 else 0.0

    fstat = fam_stats[fam_stats["family"] == sel_fam]
    cat_rmsle = float(fstat["rmsle"].iloc[0]) if len(fstat) else 0.35
    if cat_rmsle < 0.32:
        diff_label, diff_col = "Mudah diprediksi", PALETTE["green"]
    elif cat_rmsle < 0.48:
        diff_label, diff_col = "Moderat", PALETTE["amber"]
    else:
        diff_label, diff_col = "Sulit / sporadis", PALETTE["red"]

    # 4 KPI Cards
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        sign = "▲" if delta_pct >= 0 else "▼"
        dcol = PALETTE["green"] if delta_pct >= 0 else PALETTE["red"]
        st.markdown(
            render_kpi_card(
                "📦", PALETTE["cyan"], f"Total forecast {len(fc)} hari",
                fmt_id(tot_fc, 0), f"{sign} {fmt_id(abs(delta_pct), 1)}%", dcol,
                f"Toko {sel_store} · {sel_fam}",
            ),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            render_kpi_card(
                "📊", PALETTE["primary"], "Rata-rata per hari",
                fmt_id(avg_fc, 1), "± pita interval", PALETTE["violet"],
                "unit terjual / hari",
            ),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            render_kpi_card(
                "🔝", PALETTE["pink"], "Hari puncak",
                peak_str, f"{fmt_id(peak_row['sales_pred'], 0)} unit", PALETTE["pink"],
                "perkiraan tertinggi",
            ),
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            render_kpi_card(
                "🎯", diff_col, "Error kategori ini",
                f"RMSLE {fmt_id(cat_rmsle, 2)}", diff_label, diff_col,
                "benchmark validasi 15 hari",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Dual-series interactive chart
    with st.container(border=True):
        st.markdown(f"**Histori vs Forecast — Toko {sel_store} · {sel_fam}**")
        st.caption("Garis ungu = histori aktual; garis cyan putus-putus = forecast; berlian kuning = hari gajian; arsiran = rentang perkiraan wajar.")
        st.plotly_chart(plot_explorer_series(hs, fc, show_interval=show_interval, height=390), use_container_width=True)

    # Bottom section: Tabs + Export Card
    col_tbl, col_exp = st.columns([2.0, 1.0], gap="medium")
    with col_tbl:
        with st.container(border=True):
            t1, t2, t3 = st.tabs(["📋 Tabel Harian", "📆 Pola Mingguan", "🏪 Bandingkan Toko"])
            with t1:
                def _markers(r):
                    tags = []
                    if r["akhir_pekan"] == 1:
                        tags.append("Akhir pekan")
                    if r["is_payday"] == 1:
                        tags.append("Gajian")
                    if r["libur_nasional"] == 1 or r["libur_regional"] == 1 or r["libur_lokal"] == 1:
                        tags.append("Libur")
                    return " · ".join(tags) if tags else "—"

                tbl_df = pd.DataFrame(
                    {
                        "Tanggal": fc["date"].dt.strftime("%Y-%m-%d"),
                        "Hari": fc["date"].dt.dayofweek.map(lambda d: HARI_ID[d]),
                        "Forecast": fc["sales_pred"].round(1),
                        "Batas Bawah": fc["pred_lower"].round(1),
                        "Batas Atas": fc["pred_upper"].round(1),
                        "Promo": fc["onpromotion"].astype(int),
                        "Penanda": fc.apply(_markers, axis=1),
                    }
                )
                st.dataframe(tbl_df, use_container_width=True, hide_index=True, height=340)

            with t2:
                hs_dow = hs.copy()
                hs_dow["Hari"] = hs_dow["date"].dt.dayofweek.map(lambda d: HARI_ID[d])
                hs_dow["dow"] = hs_dow["date"].dt.dayofweek
                dow_summary = (
                    hs_dow.groupby(["dow", "Hari"], as_index=False)["sales"]
                    .mean()
                    .sort_values("dow")
                    .rename(columns={"sales": "Rata-rata Histori"})
                )
                fc_dow = fc.copy()
                fc_dow["dow"] = fc_dow["date"].dt.dayofweek
                fc_dow_avg = fc_dow.groupby("dow", as_index=False)["sales_pred"].mean().rename(
                    columns={"sales_pred": "Rata-rata Forecast"}
                )
                merged_dow = dow_summary.merge(fc_dow_avg, on="dow", how="left").drop(columns=["dow"])
                st.dataframe(merged_dow.round(1), use_container_width=True, hide_index=True)

            with t3:
                comp = (
                    fc_all[(fc_all["family"] == sel_fam) & (fc_all["store_nbr"].isin(avail_stores))]
                    .groupby("store_nbr", as_index=False)["sales_pred"]
                    .sum()
                    .merge(stores_df, on="store_nbr", how="left")
                    .sort_values("sales_pred", ascending=False)
                    .head(10)
                    .rename(columns={"store_nbr": "Toko", "city": "Kota", "type": "Tipe", "cluster": "Klaster", "sales_pred": "Total Forecast"})
                )
                comp["Total Forecast"] = comp["Total Forecast"].round(0)
                st.dataframe(comp, use_container_width=True, hide_index=True)

    with col_exp:
        with st.container(border=True):
            st.markdown("**📥 Ekspor & Catatan**")
            export_df = fc[["id", "date", "store_nbr", "family", "sales_pred", "pred_lower", "pred_upper", "onpromotion"]].copy()
            export_df["date"] = export_df["date"].dt.strftime("%Y-%m-%d")

            st.download_button(
                "⬇️ Unduh Forecast (CSV)",
                data=export_df.to_csv(index=False).encode("utf-8"),
                file_name=f"forecast_toko{sel_store}_{sel_fam.replace('/', '_')}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )
            st.download_button(
                "📊 Unduh Forecast (Excel .xlsx)",
                data=_to_excel_bytes(export_df),
                file_name=f"forecast_toko{sel_store}_{sel_fam.replace('/', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            st.info(
                "**Cara membaca:** Rencanakan stok mendekati **Batas Atas** untuk hari bertanda **Gajian / Akhir pekan** "
                "agar terhindar dari kehabisan stok (*stockout*)."
            )
            st.caption(
                f"Sumber: `forecast_16d.csv.gz` · Toko {sel_store} ({store_meta_map[sel_store]['city']}, "
                f"Klaster {store_meta_map[sel_store]['cluster']})"
            )
