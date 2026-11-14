# -*- coding: utf-8 -*-
"""Data loaders with Streamlit caching and real-time LightGBM scenario inference."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = APP_DIR.parent
ART_DIR = ROOT_DIR / "artifacts"


@st.cache_data(show_spinner=False)
def load_forecast() -> pd.DataFrame:
    df = pd.read_csv(ART_DIR / "forecast_16d.csv.gz", parse_dates=["date"])
    return df


@st.cache_data(show_spinner=False)
def load_history() -> pd.DataFrame:
    df = pd.read_csv(ART_DIR / "histori_90d.csv.gz", parse_dates=["date"])
    return df


@st.cache_data(show_spinner=False)
def load_stores() -> pd.DataFrame:
    return pd.read_csv(ART_DIR / "stores.csv.gz")


@st.cache_data(show_spinner=False)
def load_family_stats() -> pd.DataFrame:
    return pd.read_csv(ART_DIR / "family_stats.csv.gz")


@st.cache_data(show_spinner=False)
def load_eda_tables() -> dict[str, pd.DataFrame]:
    daily = pd.read_csv(ART_DIR / "eda_daily.csv.gz", parse_dates=["date"])
    monthly = pd.read_csv(ART_DIR / "eda_monthly.csv.gz", parse_dates=["year_month"])
    return {
        "daily": daily,
        "monthly": monthly,
        "dow": pd.read_csv(ART_DIR / "eda_dow.csv.gz"),
        "pareto": pd.read_csv(ART_DIR / "eda_pareto.csv.gz"),
        "holiday": pd.read_csv(ART_DIR / "eda_holiday.csv.gz"),
    }


@st.cache_data(show_spinner=False)
def load_model_artifacts() -> dict[str, Any]:
    with open(ART_DIR / "model_metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)
    fi = pd.read_csv(ART_DIR / "feature_importance.csv.gz")
    scatter = pd.read_csv(ART_DIR / "val_scatter.csv.gz")
    return {"metrics": metrics, "feature_importance": fi, "val_scatter": scatter}


@st.cache_data(show_spinner=False)
def load_test_features() -> pd.DataFrame:
    df = pd.read_csv(ART_DIR / "test_features.csv.gz", parse_dates=["date"])
    return df


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(ART_DIR / "model_final.joblib")


def run_whatif_inference(
    store_nbr: int,
    family: str,
    promo_override: int,
    include_payday: bool,
    include_holiday: bool,
) -> pd.DataFrame:
    """Jalankan inferensi nyata LightGBM untuk 16 hari ke depan dengan skenario pengguna."""
    meta = load_model_artifacts()["metrics"]
    fitur = meta["features_num"] + meta["features_cat"]
    feats = load_test_features()
    sub = feats[(feats["store_nbr"] == store_nbr) & (feats["family"] == family)].sort_values("date").copy()

    # Baseline prediction
    X_base = sub[fitur].copy()
    for c in meta["features_cat"]:
        X_base[c] = X_base[c].astype("category")

    model = load_model()
    base_pred = np.expm1(np.clip(model.predict(X_base), 0, None))

    # Scenario features
    X_scen = X_base.copy()
    X_scen["onpromotion"] = promo_override
    if not include_payday:
        X_scen["is_payday"] = 0
    if include_holiday:
        # Simulasikan efek hari libur nasional pada tanggal akhir pekan/tertentu atau hari tengah periode
        X_scen["libur_nasional"] = 1
    else:
        X_scen["libur_nasional"] = 0

    scen_pred = np.expm1(np.clip(model.predict(X_scen), 0, None))

    out = sub[["date", "store_nbr", "family"]].copy()
    out["baseline_promo"] = sub["onpromotion"].values
    out["scenario_promo"] = promo_override
    out["baseline_pred"] = base_pred
    out["scenario_pred"] = scen_pred
    return out.reset_index(drop=True)


def get_filtered_store_ids(stores_df: pd.DataFrame, filters: dict[str, Any]) -> list[int]:
    m = pd.Series(True, index=stores_df.index)
    if filters["types"]:
        m &= stores_df["type"].isin(filters["types"])
    if filters["state"] != "Semua provinsi (16)":
        m &= stores_df["state"] == filters["state"]
    if filters["cluster"] != "Semua klaster (1–17)":
        m &= stores_df["cluster"] == int(filters["cluster"].replace("Klaster ", ""))
    return sorted(stores_df.loc[m, "store_nbr"].astype(int).tolist())


def render_sidebar_filters() -> dict[str, Any]:
    """Render filter global dan kartu bantuan di sidebar sesuai desain FigCraft."""
    stores_df = load_stores()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div style="font-size:11px;font-weight:700;color:#64748B;letter-spacing:0.08em;margin-bottom:8px;">FILTER GLOBAL</div>',
        unsafe_allow_html=True,
    )

    fc = load_forecast()
    min_d, max_d = fc["date"].min().date(), fc["date"].max().date()
    date_range = st.sidebar.date_input(
        "Periode forecast",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d,
        help="Rentang tanggal ramalan masa depan (16–31 Agustus 2017).",
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        d_start, d_end = date_range
    else:
        d_start, d_end = min_d, max_d

    all_types = sorted(stores_df["type"].unique().tolist())
    sel_types = st.sidebar.pills(
        "Tipe toko",
        options=all_types,
        default=all_types,
        selection_mode="multi",
        help="Klasifikasi ukuran & format toko Corporación Favorita (A–E).",
    )
    if not sel_types:
        sel_types = all_types

    states = ["Semua provinsi (16)"] + sorted(stores_df["state"].unique().tolist())
    sel_state = st.sidebar.selectbox("Provinsi", states, index=0)

    clusters = ["Semua klaster (1–17)"] + [f"Klaster {c}" for c in sorted(stores_df["cluster"].unique().tolist())]
    sel_cluster = st.sidebar.selectbox("Klaster toko", clusters, index=0)

    filters = {
        "date_start": pd.Timestamp(d_start),
        "date_end": pd.Timestamp(d_end),
        "types": list(sel_types),
        "state": sel_state,
        "cluster": sel_cluster,
    }
    filters["store_ids"] = get_filtered_store_ids(stores_df, filters)

    st.sidebar.markdown(
        """
        <div class="fc-help-card">
            <h4>💡 Butuh bantuan?</h4>
            <p>Ikuti panduan langkah demi langkah atau ulangi tur interaktif untuk memahami setiap fitur.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("📘 Buka Panduan", use_container_width=True, key="sidebar_open_guide"):
        st.session_state["nav_target"] = "guide"
        st.rerun()

    st.sidebar.markdown(
        '<div class="fc-status-footer"><span class="fc-dot-green"></span>Data s/d 15 Agu 2017 · LightGBM (tuned)</div>',
        unsafe_allow_html=True,
    )
    return filters
