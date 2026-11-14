# -*- coding: utf-8 -*-
"""Halaman 3: Simulasi What-If & Safety Stock (dengan inferensi real-time LightGBM)."""
from __future__ import annotations

import math

import pandas as pd
import streamlit as st

from utils.data_loader import load_family_stats, load_forecast, load_stores, run_whatif_inference
from utils.plotting import plot_whatif_comparison
from utils.styles import PALETTE, fmt_id, render_kpi_card, render_page_header
from utils.tour import render_tour_banner

SERVICE_Z = {"90%": 1.28, "95%": 1.65, "99%": 2.33}


def render_simulator(filters: dict) -> None:
    render_tour_banner()

    top_l, top_r = st.columns([3.5, 1.3])
    with top_l:
        render_page_header(
            "Beranda / Simulasi What-If",
            "Simulasi What-If & Safety Stock",
            "Uji skenario promosi dengan model LightGBM dan hitung persediaan pengaman yang direkomendasikan sebelum membuat pesanan ke pemasok.",
        )
    with top_r:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("🔁 Reset Skenario", use_container_width=True):
            st.session_state["saved_scenarios"] = []
            st.toast("Daftar skenario direset.", icon="🔁")
            st.rerun()

    stores_df = load_stores()
    fc_all = load_forecast()
    fam_stats = load_family_stats()
    avail_stores = filters["store_ids"] or sorted(stores_df["store_nbr"].astype(int).tolist())
    store_meta_map = stores_df.set_index("store_nbr").to_dict("index")
    all_families = sorted(fc_all["family"].unique().tolist())

    default_store = 44 if 44 in avail_stores else avail_stores[0]
    default_fam_idx = all_families.index("GROCERY I") if "GROCERY I" in all_families else 0

    if "saved_scenarios" not in st.session_state:
        st.session_state["saved_scenarios"] = []

    col_ctl, col_res = st.columns([1.0, 1.95], gap="large")

    with col_ctl:
        with st.container(border=True):
            st.markdown("**🎛️ Parameter Skenario**")
            st.caption("Ubah nilai lalu lihat dampaknya secara langsung.")

            sel_store = st.selectbox(
                "Toko",
                options=avail_stores,
                index=avail_stores.index(default_store),
                format_func=lambda s: f"Toko {s} · {store_meta_map[s]['city']} · Tipe {store_meta_map[s]['type']}",
                key="sim_store",
            )
            sel_fam = st.selectbox("Kategori produk", options=all_families, index=default_fam_idx, key="sim_fam")

            base_sub = fc_all[(fc_all["store_nbr"] == sel_store) & (fc_all["family"] == sel_fam)]
            base_promo_avg = int(round(base_sub["onpromotion"].mean())) if len(base_sub) else 10
            max_promo = max(60, base_promo_avg * 3, int(base_sub["onpromotion"].max()) * 2 if len(base_sub) else 60)

            promo_val = st.slider(
                f"Jumlah item promo / hari (baseline ≈ {base_promo_avg})",
                min_value=0,
                max_value=int(max_promo),
                value=min(int(max_promo), max(base_promo_avg + 10, 15)),
                step=1,
            )
            lead_time = st.slider("Lead time pemasok (hari)", min_value=1, max_value=14, value=3, step=1)

            service_lvl = st.segmented_control(
                "Service level (tingkat layanan)",
                options=["90%", "95%", "99%"],
                default="95%",
            ) or "95%"
            z_val = SERVICE_Z[service_lvl]
            st.caption(f"Z = {fmt_id(z_val, 2)} → peluang tidak kehabisan stok {service_lvl}")

            include_payday = st.toggle("Pertahankan efek hari gajian", value=True, help="Tanggal 15 & akhir bulan")
            include_holiday = st.toggle("Simulasikan hari libur nasional", value=False)
            show_baseline = st.toggle("Bandingkan dengan baseline", value=True)

            scen_name = st.text_input("Nama skenario", value=f"Promo {promo_val} · LT {lead_time}h")
            save_clicked = st.button("💾 Simpan Skenario ke Tabel", type="primary", use_container_width=True)

    # Jalankan inferensi real-time LightGBM
    sim_df = run_whatif_inference(sel_store, sel_fam, promo_val, include_payday, include_holiday)
    base_tot = float(sim_df["baseline_pred"].sum())
    scen_tot = float(sim_df["scenario_pred"].sum())
    diff_units = scen_tot - base_tot
    lift_pct = ((scen_tot / base_tot) - 1.0) * 100.0 if base_tot > 0 else 0.0

    # Statistik residual kategori untuk Safety Stock
    fstat = fam_stats[fam_stats["family"] == sel_fam]
    sigma_cat = float(fstat["sigma_daily"].iloc[0]) if len(fstat) else float(sim_df["scenario_pred"].std() + 10.0)
    mean_val_sales = float(fstat["mean_val_sales"].iloc[0]) if len(fstat) else 1.0
    # Skalakan sigma terhadap ukuran toko saat ini
    daily_scen = scen_tot / max(len(sim_df), 1)
    scale_factor = (daily_scen / mean_val_sales) if mean_val_sales > 0 else 1.0
    sigma_scaled = max(sigma_cat * min(max(scale_factor, 0.2), 4.0), 1.0)

    safety_stock = z_val * sigma_scaled * math.sqrt(lead_time)
    reorder_point = daily_scen * lead_time + safety_stock
    risk_pct = (1.0 - float(service_lvl.replace("%", "")) / 100.0) * 100.0
    if risk_pct <= 2.0:
        risk_lbl, risk_col = "Sangat Rendah", PALETTE["green"]
    elif risk_pct <= 6.0:
        risk_lbl, risk_col = "Rendah", PALETTE["green"]
    else:
        risk_lbl, risk_col = "Sedang", PALETTE["amber"]

    if save_clicked:
        st.session_state["saved_scenarios"].append(
            {
                "Skenario": scen_name,
                "Toko & Kategori": f"#{sel_store} · {sel_fam}",
                "Promo": promo_val,
                "Lead time": f"{lead_time} hari",
                "Service": service_lvl,
                "Total Forecast": round(scen_tot, 0),
                "Delta vs Baseline": f"{'+' if diff_units >= 0 else ''}{fmt_id(diff_units, 0)}",
                "Safety Stock": round(safety_stock, 0),
            }
        )
        st.toast(f"Skenario '{scen_name}' disimpan!", icon="✅")

    with col_res:
        k1, k2, k3, k4 = st.columns(4, gap="medium")
        with k1:
            sign = "+" if lift_pct >= 0 else ""
            lcol = PALETTE["pink"] if lift_pct >= 0 else PALETTE["red"]
            st.markdown(
                render_kpi_card(
                    "🚀", PALETTE["pink"], "Lift penjualan",
                    f"{sign}{fmt_id(lift_pct, 1)}%",
                    f"{'+' if diff_units >= 0 else ''}{fmt_id(diff_units, 0)} unit", lcol,
                ),
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                render_kpi_card(
                    "🛡️", PALETTE["cyan"], "Safety stock",
                    fmt_id(safety_stock, 0), "unit cadangan", PALETTE["cyan"],
                ),
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                render_kpi_card(
                    "📍", PALETTE["primary"], "Reorder point",
                    fmt_id(reorder_point, 0), "pesan ulang ≤", PALETTE["violet"],
                ),
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                render_kpi_card(
                    "🟢", risk_col, "Risiko stockout",
                    risk_lbl, f"{fmt_id(risk_pct, 1)}% peluang", risk_col,
                ),
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"**Baseline vs Skenario — Toko {sel_store} · {sel_fam} (16 Hari)**")
            st.caption("Prediksi harian hasil inferensi langsung model LightGBM (tuned).")
            st.plotly_chart(plot_whatif_comparison(sim_df, show_baseline=show_baseline, height=340), use_container_width=True)

        c_f, c_b = st.columns([1.2, 1.0], gap="medium")
        with c_f:
            with st.container(border=True):
                st.markdown("**🧮 Rumus Safety Stock**")
                st.markdown('<div class="fc-formula">SS = Z × σ × √L</div>', unsafe_allow_html=True)
                st.caption(
                    f"Z = {fmt_id(z_val, 2)} (service level {service_lvl}) · "
                    f"σ = {fmt_id(sigma_scaled, 1)} unit/hari · L = {lead_time} hari → "
                    f"**{fmt_id(safety_stock, 0)} unit**"
                )
        with c_b:
            with st.container(border=True):
                st.markdown("**🧯 Buffer per Tipe Kategori**")
                st.caption("Rekomendasi berdasarkan volatilitas error")
                st.markdown("**PRODUCE / MEATS (segar)** — *Sedang (+15%)*")
                st.progress(0.55)
                st.markdown("**DAIRY / GROCERY I (stabil)** — *Rendah (+10%)*")
                st.progress(0.35)
                st.markdown("**SCHOOL & OFFICE (sporadis)** — *Tinggi (+40%)*")
                st.progress(0.92)

    st.warning(
        "**Catatan Penting:** Efek promosi pada model bersifat **asosiatif** (dipelajari dari data historis 2015–2017), "
        "bukan kausal murni. Gunakan hasil simulasi sebagai panduan arah dan evaluasi ulang setelah promo berjalan."
    )

    with st.container(border=True):
        st.markdown("**💾 Skenario Tersimpan**")
        if st.session_state["saved_scenarios"]:
            sc_df = pd.DataFrame(st.session_state["saved_scenarios"])
            st.dataframe(sc_df, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 Unduh Perbandingan Skenario (CSV)",
                data=sc_df.to_csv(index=False).encode("utf-8"),
                file_name="perbandingan_skenario_whatif.csv",
                mime="text/csv",
            )
        else:
            st.info("Belum ada skenario yang disimpan. Atur parameter di panel kiri lalu klik **Simpan Skenario ke Tabel**.")
