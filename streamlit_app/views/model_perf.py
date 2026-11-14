# -*- coding: utf-8 -*-
"""Halaman 5: Performa & Transparansi Model."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import load_family_stats, load_model_artifacts
from utils.plotting import plot_actual_vs_pred, plot_horizontal_bars, plot_overfitting_check
from utils.styles import PALETTE, fmt_id, render_page_header
from utils.tour import render_tour_banner


def render_model_perf(filters: dict) -> None:
    render_tour_banner()
    render_page_header(
        "Beranda / Performa Model",
        "Performa & Transparansi Model",
        "Perbandingan 6 model pada validasi 15 hari terakhir (1–15 Agu 2017), faktor pendorong prediksi, analisis error per kategori, serta cek overfitting.",
    )

    art = load_model_artifacts()
    meta = art["metrics"]
    fi = art["feature_importance"]
    scatter = art["val_scatter"]
    fam_stats = load_family_stats()

    lb_df = pd.DataFrame(meta["leaderboard"]).sort_values("RMSLE").reset_index(drop=True)
    best = lb_df[lb_df["model"] == meta["best_model"]].iloc[0]
    base_best = lb_df[lb_df["model"].str.startswith("Baseline")]["RMSLE"].min()
    improve_pct = (1.0 - best["RMSLE"] / base_best) * 100.0

    # Champion Banner
    st.markdown(
        f"""
        <div class="fc-champion">
            <div>
                <div class="fc-champion-title">🏆 Model Terpilih: {meta['best_model']}</div>
                <div class="fc-champion-sub">
                    RMSLE {fmt_id(best['RMSLE'], 4)} · {fmt_id(improve_pct, 1)}% lebih rendah dari baseline terbaik ·
                    dilatih pada {fmt_id(meta['train_rows'])} baris data (2015–2017).
                </div>
            </div>
            <div class="fc-champion-stats">
                <div>
                    <div class="fc-champion-stat-val">{fmt_id(best['R2'], 3)}</div>
                    <div class="fc-champion-stat-lbl">R²</div>
                </div>
                <div>
                    <div class="fc-champion-stat-val">{fmt_id(best['MAE'], 1)}</div>
                    <div class="fc-champion-stat-lbl">MAE</div>
                </div>
                <div>
                    <div class="fc-champion-stat-val">{fmt_id(best['WAPE'] * 100, 1)}%</div>
                    <div class="fc-champion-stat-lbl">WAPE</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Leaderboard Table
    with st.container(border=True):
        hdr_l, hdr_r = st.columns([3.0, 1.0])
        with hdr_l:
            st.markdown("**📋 Leaderboard Perbandingan Model**")
            st.caption("Diurutkan dari RMSLE validasi terendah (semakin kecil semakin akurat).")
        with hdr_r:
            st.download_button(
                "📄 Unduh CSV Leaderboard",
                data=lb_df.to_csv(index=False).encode("utf-8"),
                file_name="leaderboard_model.csv",
                mime="text/csv",
                use_container_width=True,
            )

        medals = ["🥇 ", "🥈 ", "🥉 "]
        disp_lb = pd.DataFrame(
            {
                "Model": [f"{medals[i] if i < 3 else ''}{m}" for i, m in enumerate(lb_df["model"])],
                "RMSLE Validasi ↓": lb_df["RMSLE"].round(4),
                "RMSE": lb_df["RMSE"].round(2),
                "MAE": lb_df["MAE"].round(2),
                "R²": lb_df["R2"].round(4),
                "WAPE (%)": (lb_df["WAPE"] * 100).round(2),
                "Waktu Latih (dtk)": lb_df["waktu_train_detik"].map(lambda x: f"{x:.1f}" if x > 0 else "—"),
            }
        )
        st.dataframe(disp_lb, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Row 2: Feature Importance + Group Contribution & Hard/Easy Categories
    c_fi, c_side = st.columns([1.3, 1.0], gap="medium")
    with c_fi:
        with st.container(border=True):
            st.markdown("**🔍 Feature Importance (Gain) — Top 10**")
            st.caption("Kontribusi relatif masing-masing fitur dalam model LightGBM (tuned).")
            top10 = fi.head(10)
            bar_cols = [
                PALETTE["primary"] if "roll" in f else (PALETTE["violet"] if "lag" in f or "dow" in f else (PALETTE["pink"] if "promo" in f else PALETTE["cyan"]))
                for f in top10["fitur"]
            ]
            st.plotly_chart(
                plot_horizontal_bars(
                    top10["fitur"].tolist(),
                    top10["kontribusi_pct"].tolist(),
                    colors=bar_cols,
                    unit_suffix="%",
                    height=380,
                ),
                use_container_width=True,
            )

    with c_side:
        with st.container(border=True):
            st.markdown("**🧩 Kontribusi per Kelompok Fitur**")
            grp = fi.groupby("kelompok", as_index=False)["kontribusi_pct"].sum().sort_values("kontribusi_pct", ascending=False)
            grp_cols = [PALETTE["primary"], PALETTE["amber"], PALETTE["violet"], PALETTE["pink"], PALETTE["cyan"], PALETTE["green"]]
            st.plotly_chart(
                plot_horizontal_bars(
                    grp["kelompok"].tolist(),
                    grp["kontribusi_pct"].tolist(),
                    colors=grp_cols[: len(grp)],
                    unit_suffix="%",
                    height=225,
                ),
                use_container_width=True,
            )

        with st.container(border=True):
            st.markdown("**🎯 Kategori Tersulit vs Termudah Diprediksi**")
            st.caption("Berdasarkan RMSLE pada validasi 15 hari terakhir")
            hardest = fam_stats.sort_values("rmsle", ascending=False).head(3)
            easiest = fam_stats.sort_values("rmsle", ascending=True).head(3)
            cl_h, cl_e = st.columns(2)
            with cl_h:
                st.markdown("**🔴 Tersulit (RMSLE Tinggi)**")
                for _, r in hardest.iterrows():
                    st.markdown(f"- **{r['family']}** (`{r['rmsle']:.2f}` · {r['zero_share']*100:.0f}% nol)")
            with cl_e:
                st.markdown("**🟢 Termudah (RMSLE Rendah)**")
                for _, r in easiest.iterrows():
                    st.markdown(f"- **{r['family']}** (`{r['rmsle']:.2f}` · {r['zero_share']*100:.0f}% nol)")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Row 3: Actual vs Predicted + Overfitting Check
    b_l, b_r = st.columns(2, gap="medium")
    with b_l:
        with st.container(border=True):
            st.markdown("**📍 Aktual vs Prediksi (Sampel Validasi)**")
            st.caption("Skala log1p(sales). Titik yang rapat di sekitar garis merah menandakan prediksi akurat.")
            st.plotly_chart(plot_actual_vs_pred(scatter, height=330), use_container_width=True)
    with b_r:
        with st.container(border=True):
            st.markdown("**🧪 Cek Overfitting (RMSLE Train vs Validasi)**")
            st.caption("Selisih kecil antara Train dan Validasi menunjukkan model menggeneralisasi dengan baik.")
            st.plotly_chart(plot_overfitting_check(lb_df, height=330), use_container_width=True)
