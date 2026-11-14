# -*- coding: utf-8 -*-
"""
Ekstraksi artefak model & ringkasan data dari dataset Store Sales (Corporacion Favorita)
mengikuti pipeline MiniProject_StoreSalesRegression_Kelompok7.ipynb.

Jalankan:
    python scripts/export_artifacts.py
"""
from __future__ import annotations

import json
import os
import time
import warnings
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "store-sales-time-series-forecasting-20261114T114828Z-1-001" / "store-sales-time-series-forecasting"
ART_DIR = ROOT / "artifacts"
ART_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
START_DATE = "2015-01-01"
VAL_DAYS = 15
GEMPA = pd.Timestamp("2016-04-16")


def save_df(df: pd.DataFrame, name: str) -> None:
    df.to_csv(ART_DIR / f"{name}.csv.gz", index=False, compression="gzip")


def bersihkan_libur(h: pd.DataFrame) -> pd.DataFrame:
    h = h.copy()
    h["date"] = pd.to_datetime(h["date"])
    h = h[~h["transferred"].astype(bool)]
    h["jenis"] = np.select(
        [
            h["type"].isin(["Holiday", "Transfer", "Additional", "Bridge"]),
            h["type"].eq("Work Day"),
            h["type"].eq("Event"),
        ],
        ["libur", "hari_kerja_pengganti", "event"],
        default="lain",
    )
    return h[["date", "type", "locale", "locale_name", "description", "jenis"]]


def hitung_metrik(y_log_true, pred_log) -> dict[str, float]:
    pred_log = np.clip(np.asarray(pred_log, dtype="float64"), 0, None)
    y_log_true = np.asarray(y_log_true, dtype="float64")
    y, p = np.expm1(y_log_true), np.expm1(pred_log)
    return {
        "RMSLE": float(np.sqrt(mean_squared_error(y_log_true, pred_log))),
        "RMSE": float(np.sqrt(mean_squared_error(y, p))),
        "MAE": float(mean_absolute_error(y, p)),
        "R2": float(r2_score(y, p)),
        "WAPE": float(np.abs(y - p).sum() / max(y.sum(), 1e-9)),
    }


def main() -> None:
    t0 = time.time()
    print(f"Membaca dataset dari: {DATA_DIR}")
    train = pd.read_csv(
        DATA_DIR / "train.csv",
        parse_dates=["date"],
        dtype={"id": "int32", "store_nbr": "int16", "family": "category", "sales": "float32", "onpromotion": "int16"},
    )
    test = pd.read_csv(
        DATA_DIR / "test.csv",
        parse_dates=["date"],
        dtype={"id": "int32", "store_nbr": "int16", "family": "category", "onpromotion": "int16"},
    )
    stores = pd.read_csv(DATA_DIR / "stores.csv")
    oil = pd.read_csv(DATA_DIR / "oil.csv", parse_dates=["date"])
    holidays = pd.read_csv(DATA_DIR / "holidays_events.csv", parse_dates=["date"])
    transactions = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["date"])

    lib = bersihkan_libur(holidays)
    libur_only = lib[lib["jenis"] == "libur"]

    # ------------------------------------------------------------------
    # 1. Ekstrak Ringkasan EDA (dari seluruh data 2013-2017)
    # ------------------------------------------------------------------
    print("Mengekstrak data EDA...")
    train_eda = train.copy()
    train_eda["family"] = train_eda["family"].astype(str)

    # Harian nasional + oil + holiday flags
    harian = train_eda.groupby("date", as_index=False).agg(
        sales=("sales", "sum"),
        onpromotion=("onpromotion", "sum"),
    )
    trx_daily = transactions.groupby("date", as_index=False)["transactions"].sum()
    oil_full = oil.set_index("date")["dcoilwtico"].reindex(pd.date_range(train_eda["date"].min(), test["date"].max())).ffill().bfill()
    oil_df = oil_full.reset_index().rename(columns={"index": "date", "dcoilwtico": "oil_price"})

    tgl_libur_nas = pd.DatetimeIndex(libur_only[libur_only["locale"] == "National"]["date"].unique())
    tgl_event_nas = pd.DatetimeIndex(lib[(lib["jenis"] == "event") & (lib["locale"] == "National")]["date"].unique())
    tgl_workday = pd.DatetimeIndex(lib[lib["jenis"] == "hari_kerja_pengganti"]["date"].unique())

    eda_daily = harian.merge(trx_daily, on="date", how="left").merge(oil_df, on="date", how="left")
    eda_daily["tren_29"] = eda_daily["sales"].rolling(29, center=True, min_periods=15).mean()
    eda_daily["rasio_tren"] = np.where(eda_daily["tren_29"] > 0, eda_daily["sales"] / eda_daily["tren_29"], np.nan)
    eda_daily["dow"] = eda_daily["date"].dt.dayofweek
    eda_daily["is_weekend"] = eda_daily["dow"] >= 5
    eda_daily["is_payday"] = (eda_daily["date"].dt.day == 15) | eda_daily["date"].dt.is_month_end
    eda_daily["kelompok_hari"] = "Hari biasa"
    eda_daily.loc[eda_daily["date"].isin(tgl_event_nas), "kelompok_hari"] = "Event nasional"
    eda_daily.loc[eda_daily["date"].isin(tgl_workday), "kelompok_hari"] = "Hari kerja pengganti"
    eda_daily.loc[eda_daily["date"].isin(tgl_libur_nas), "kelompok_hari"] = "Libur nasional"
    save_df(eda_daily, "eda_daily")

    # Bulanan
    eda_monthly = (
        eda_daily.assign(year_month=eda_daily["date"].dt.to_period("M").dt.to_timestamp())
        .groupby("year_month", as_index=False)
        .agg(sales=("sales", "sum"), oil_price=("oil_price", "mean"), transactions=("transactions", "sum"))
    )
    save_df(eda_monthly, "eda_monthly")

    # Day of week index
    dow_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    eda_dow = (
        eda_daily[eda_daily["sales"] > 0]
        .groupby("dow", as_index=False)["sales"]
        .mean()
        .sort_values("dow")
    )
    eda_dow["hari"] = [dow_names[i] for i in eda_dow["dow"]]
    eda_dow["indeks"] = eda_dow["sales"] / eda_dow["sales"].iloc[0] * 100.0
    save_df(eda_dow, "eda_dow")

    # Pareto per family + proporsi nol + promo lift
    fam_agg = train_eda.groupby("family", as_index=False).agg(
        total_sales=("sales", "sum"),
        mean_sales=("sales", "mean"),
        zero_share=("sales", lambda s: float((s == 0).mean())),
    )
    promo_yes = train_eda[train_eda["onpromotion"] > 0].groupby("family")["sales"].mean()
    promo_no = train_eda[train_eda["onpromotion"] == 0].groupby("family")["sales"].mean()
    fam_agg["sales_promo"] = fam_agg["family"].map(promo_yes).fillna(0.0)
    fam_agg["sales_no_promo"] = fam_agg["family"].map(promo_no).fillna(0.0)
    fam_agg["promo_lift_ratio"] = np.where(
        fam_agg["sales_no_promo"] > 0,
        fam_agg["sales_promo"] / fam_agg["sales_no_promo"],
        1.0,
    )
    fam_agg = fam_agg.sort_values("total_sales", ascending=False).reset_index(drop=True)
    fam_agg["share_pct"] = fam_agg["total_sales"] / fam_agg["total_sales"].sum() * 100.0
    fam_agg["cum_share_pct"] = fam_agg["share_pct"].cumsum()
    save_df(fam_agg, "eda_pareto")

    # Holiday summary
    eda_holiday = (
        eda_daily[eda_daily["sales"] > 0]
        .dropna(subset=["rasio_tren"])
        .groupby("kelompok_hari", as_index=False)
        .agg(jumlah_hari=("rasio_tren", "count"), median_rasio=("rasio_tren", "median"), mean_rasio=("rasio_tren", "mean"))
    )
    save_df(eda_holiday, "eda_holiday")

    save_df(stores, "stores")
    del train_eda

    # ------------------------------------------------------------------
    # 2. Feature Engineering (persis seperti Notebook Bagian 4)
    # ------------------------------------------------------------------
    print("Membangun fitur deret waktu (anti-leakage)...")
    tes = test.copy()
    tes["sales"] = np.nan
    gab = pd.concat([train, tes], ignore_index=True)
    gab["family"] = gab["family"].astype(str)
    gab["store_nbr"] = gab["store_nbr"].astype("int64")

    TRAIN_END = train["date"].max()
    TANGGAL = pd.date_range(gab["date"].min(), gab["date"].max())
    TOKO = sorted(gab["store_nbr"].unique())
    FAMILY = sorted(gab["family"].unique())
    N_SERIES, T = len(TOKO) * len(FAMILY), len(TANGGAL)

    idx = pd.MultiIndex.from_product([TOKO, FAMILY, TANGGAL], names=["store_nbr", "family", "date"])
    df = gab.set_index(["store_nbr", "family", "date"]).reindex(idx).reset_index()
    df["onpromotion"] = df["onpromotion"].fillna(0)
    del gab

    Y = pd.DataFrame(np.log1p(df["sales"].values.reshape(N_SERIES, T).T), index=TANGGAL)

    def ke_kolom(W):
        return W.values.T.ravel().astype("float32")

    F = {}
    for k in [16, 21, 28, 35, 364]:
        F[f"lag_{k}"] = ke_kolom(Y.shift(k))

    S = Y.shift(16)
    for w in [7, 14, 28]:
        F[f"roll_mean_{w}"] = ke_kolom(S.rolling(w, min_periods=max(1, w // 2)).mean())
    for w in [7, 28]:
        F[f"roll_std_{w}"] = ke_kolom(S.rolling(w, min_periods=max(2, w // 2)).std())

    Z = (Y == 0).astype(float).where(Y.notna())
    F["zero_share_28"] = ke_kolom(Z.shift(16).rolling(28, min_periods=14).mean())

    F_lag = pd.DataFrame({k: F[k] for k in ["lag_21", "lag_28", "lag_35"]})
    F["dow_mean_3"] = F_lag.mean(axis=1).values.astype("float32")
    F["selisih_7_28"] = (F["roll_mean_7"] - F["roll_mean_28"]).astype("float32")
    del Y, S, Z, F_lag

    kal = pd.DataFrame(index=TANGGAL)
    kal["bulan"] = TANGGAL.month
    kal["hari"] = TANGGAL.day
    kal["hari_minggu"] = TANGGAL.dayofweek
    kal["minggu_tahun"] = TANGGAL.isocalendar().week.to_numpy().astype(int)
    kal["akhir_pekan"] = (TANGGAL.dayofweek >= 5).astype(int)
    kal["is_month_start"] = TANGGAL.is_month_start.astype(int)
    kal["is_month_end"] = TANGGAL.is_month_end.astype(int)
    kal["is_payday"] = ((TANGGAL.day == 15) | TANGGAL.is_month_end).astype(int)
    kal["dow_sin"] = np.sin(2 * np.pi * kal["hari_minggu"] / 7)
    kal["dow_cos"] = np.cos(2 * np.pi * kal["hari_minggu"] / 7)
    kal["month_sin"] = np.sin(2 * np.pi * kal["bulan"] / 12)
    kal["month_cos"] = np.cos(2 * np.pi * kal["bulan"] / 12)

    nat = pd.DatetimeIndex(libur_only[libur_only["locale"] == "National"]["date"].unique())
    kal["libur_nasional"] = TANGGAL.isin(nat).astype(int)
    kal["libur_besok"] = (TANGGAL + pd.Timedelta(days=1)).isin(nat).astype(int)
    kal["libur_kemarin"] = (TANGGAL - pd.Timedelta(days=1)).isin(nat).astype(int)
    kal["event_nasional"] = TANGGAL.isin(tgl_event_nas).astype(int)
    kal["hari_kerja_pengganti"] = TANGGAL.isin(tgl_workday).astype(int)
    kal["pasca_gempa"] = ((TANGGAL >= GEMPA) & (TANGGAL <= GEMPA + pd.Timedelta(days=30))).astype(int)

    oil_d = oil.set_index("date")["dcoilwtico"].reindex(TANGGAL).ffill().bfill()
    kal["oil_lag16"] = oil_d.shift(16).values
    kal["oil_ma7_lag16"] = oil_d.shift(16).rolling(7, min_periods=1).mean().values

    pos_d = np.tile(np.arange(T), N_SERIES)
    for c in kal.columns:
        F[c] = kal[c].values[pos_d].astype("float32" if kal[c].dtype.kind == "f" else "int8")

    toko_info = stores.set_index("store_nbr").loc[TOKO]
    reg_mat = np.zeros((len(TOKO), T), dtype=np.int8)
    loc_mat = np.zeros((len(TOKO), T), dtype=np.int8)
    for i, (_, r) in enumerate(toko_info.iterrows()):
        reg_mat[i] = TANGGAL.isin(libur_only[(libur_only["locale"] == "Regional") & (libur_only["locale_name"] == r["state"])]["date"])
        loc_mat[i] = TANGGAL.isin(libur_only[(libur_only["locale"] == "Local") & (libur_only["locale_name"] == r["city"])]["date"])
    F["libur_regional"] = np.repeat(reg_mat, len(FAMILY), axis=0).ravel()
    F["libur_lokal"] = np.repeat(loc_mat, len(FAMILY), axis=0).ravel()

    def ekspansi_toko(nilai):
        return np.repeat(np.repeat(np.asarray(nilai), len(FAMILY)), T)

    F["tipe_toko"] = ekspansi_toko(toko_info["type"].values)
    F["city"] = ekspansi_toko(toko_info["city"].values)
    F["state"] = ekspansi_toko(toko_info["state"].values)
    F["cluster"] = ekspansi_toko(toko_info["cluster"].values).astype("int16")

    trx_w = transactions.pivot_table(index="date", columns="store_nbr", values="transactions").reindex(index=TANGGAL, columns=TOKO)
    trx_roll = trx_w.shift(16).rolling(28, min_periods=7).mean()
    F["trans_roll28_lag16"] = np.repeat(trx_roll.values.T, len(FAMILY), axis=0).ravel().astype("float32")

    df = pd.concat([df, pd.DataFrame(F, index=df.index)], axis=1)
    del F
    df["y"] = np.log1p(df["sales"]).astype("float32")
    df["is_test"] = df["date"] > TRAIN_END
    for c in ["store_nbr", "family", "tipe_toko", "city", "state"]:
        df[c] = df[c].astype("category")

    df_model = df[(df["date"] >= START_DATE) & (df["is_test"] | df["sales"].notna())].copy()
    df_model = df_model.sort_values(["date", "store_nbr", "family"]).reset_index(drop=True)
    del df

    FITUR_NUM = [
        "onpromotion", "cluster",
        "lag_16", "lag_21", "lag_28", "lag_35", "lag_364",
        "roll_mean_7", "roll_mean_14", "roll_mean_28", "roll_std_7", "roll_std_28",
        "zero_share_28", "dow_mean_3", "selisih_7_28", "trans_roll28_lag16",
        "oil_lag16", "oil_ma7_lag16",
        "bulan", "hari", "hari_minggu", "minggu_tahun", "akhir_pekan",
        "is_payday", "is_month_start", "is_month_end",
        "dow_sin", "dow_cos", "month_sin", "month_cos",
        "libur_nasional", "libur_regional", "libur_lokal", "libur_besok", "libur_kemarin",
        "event_nasional", "hari_kerja_pengganti", "pasca_gempa",
    ]
    FITUR_CAT = ["store_nbr", "family", "tipe_toko", "city", "state"]
    FITUR = FITUR_NUM + FITUR_CAT

    # ------------------------------------------------------------------
    # 3. Validasi Model (15 hari terakhir: 2017-08-01 s/d 2017-08-15)
    # ------------------------------------------------------------------
    VAL_START = TRAIN_END - pd.Timedelta(days=VAL_DAYS - 1)
    tr_mask = (~df_model["is_test"]) & (df_model["date"] < VAL_START)
    va_mask = (~df_model["is_test"]) & (df_model["date"] >= VAL_START)
    all_tr_mask = ~df_model["is_test"]
    te_mask = df_model["is_test"]

    X_tr, y_tr = df_model.loc[tr_mask, FITUR], df_model.loc[tr_mask, "y"]
    X_va, y_va = df_model.loc[va_mask, FITUR], df_model.loc[va_mask, "y"]
    va_df = df_model.loc[va_mask, ["date", "store_nbr", "family", "sales", "y"]].copy()

    leaderboard = []

    # Baseline 1 & 2
    b1 = X_va["lag_21"].fillna(X_va["roll_mean_28"]).fillna(0)
    b2 = X_va["roll_mean_28"].fillna(0)
    leaderboard.append({"model": "Baseline: Seasonal Naive (lag_21)", **hitung_metrik(y_va, b1), "RMSLE_train": np.nan, "waktu_train_detik": 0.0})
    leaderboard.append({"model": "Baseline: Rata-rata 28 hari", **hitung_metrik(y_va, b2), "RMSLE_train": np.nan, "waktu_train_detik": 0.0})

    # Ridge
    print("Melatih Ridge Regression...")
    t_s = time.time()
    pre_ridge = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), FITUR_NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), FITUR_CAT),
    ])
    m_ridge = Pipeline([("pre", pre_ridge), ("model", Ridge(alpha=1.0))])
    m_ridge.fit(X_tr, y_tr)
    dt_r = time.time() - t_s
    m_tr_r = hitung_metrik(y_tr, m_ridge.predict(X_tr))
    leaderboard.append({"model": "Ridge", **hitung_metrik(y_va, m_ridge.predict(X_va)), "RMSLE_train": m_tr_r["RMSLE"], "waktu_train_detik": round(dt_r, 1)})

    # Random Forest (200k latest rows, persis notebook)
    print("Melatih Random Forest (200k baris terbaru)...")
    t_s = time.time()
    pre_rf = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), FITUR_NUM),
        ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), FITUR_CAT),
    ])
    m_rf = Pipeline([("pre", pre_rf), ("model", RandomForestRegressor(n_estimators=40, max_depth=16, min_samples_leaf=20, max_samples=0.7, random_state=SEED, n_jobs=-1))])
    X_rf_tr, y_rf_tr = X_tr.iloc[-200_000:], y_tr.iloc[-200_000:]
    m_rf.fit(X_rf_tr, y_rf_tr)
    dt_rf = time.time() - t_s
    m_tr_rf = hitung_metrik(y_rf_tr, m_rf.predict(X_rf_tr))
    leaderboard.append({"model": "Random Forest", **hitung_metrik(y_va, m_rf.predict(X_va)), "RMSLE_train": m_tr_rf["RMSLE"], "waktu_train_detik": round(dt_rf, 1)})

    # LightGBM Default
    print("Melatih LightGBM (default)...")
    t_s = time.time()
    m_lgb = lgb.LGBMRegressor(
        n_estimators=500, learning_rate=0.05, num_leaves=63, min_child_samples=50,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0,
        importance_type="gain", random_state=SEED, n_jobs=-1, verbose=-1,
    )
    m_lgb.fit(X_tr, y_tr)
    dt_l = time.time() - t_s
    m_tr_l = hitung_metrik(y_tr, m_lgb.predict(X_tr))
    leaderboard.append({"model": "LightGBM", **hitung_metrik(y_va, m_lgb.predict(X_va)), "RMSLE_train": m_tr_l["RMSLE"], "waktu_train_detik": round(dt_l, 1)})

    # LightGBM Tuned (parameter terbaik hasil tuning notebook)
    print("Melatih LightGBM (tuned)...")
    t_s = time.time()
    best_params = dict(
        n_estimators=700, learning_rate=0.03, num_leaves=63, min_child_samples=20,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=5.0,
        importance_type="gain", random_state=SEED, n_jobs=-1, verbose=-1,
    )
    m_tuned = lgb.LGBMRegressor(**best_params)
    m_tuned.fit(X_tr, y_tr)
    dt_lt = time.time() - t_s
    pred_va_log = np.clip(m_tuned.predict(X_va), 0, None)
    m_tr_lt = hitung_metrik(y_tr, m_tuned.predict(X_tr))
    leaderboard.append({"model": "LightGBM (tuned)", **hitung_metrik(y_va, pred_va_log), "RMSLE_train": m_tr_lt["RMSLE"], "waktu_train_detik": round(dt_lt, 1)})

    lb_df = pd.DataFrame(leaderboard).sort_values("RMSLE").reset_index(drop=True)
    print("\nLeaderboard:\n", lb_df[["model", "RMSLE", "WAPE", "MAE", "R2", "waktu_train_detik"]].round(4))

    # Statistik error & residual per kategori (untuk Safety Stock & Transparansi)
    va_df["pred_sales"] = np.expm1(pred_va_log)
    va_df["pred_log"] = pred_va_log
    va_df["err2"] = (va_df["pred_log"] - va_df["y"]) ** 2
    va_df["abs_err"] = (va_df["pred_sales"] - va_df["sales"]).abs()
    va_df["residual"] = va_df["sales"] - va_df["pred_sales"]
    va_df["family"] = va_df["family"].astype(str)
    va_df["store_nbr"] = va_df["store_nbr"].astype(int)

    fam_val = va_df.groupby("family", as_index=False).agg(
        rmsle=("err2", lambda s: float(np.sqrt(s.mean()))),
        mae=("abs_err", "mean"),
        sigma_daily=("residual", "std"),
        mean_val_sales=("sales", "mean"),
        total_val_sales=("sales", "sum"),
        total_abs_err=("abs_err", "sum"),
    )
    fam_val["wape"] = np.where(fam_val["total_val_sales"] > 0, fam_val["total_abs_err"] / fam_val["total_val_sales"], np.nan)
    fam_stats = fam_val.merge(
        fam_agg[["family", "zero_share", "promo_lift_ratio", "total_sales"]],
        on="family",
        how="left",
    )
    fam_stats["sigma_daily"] = fam_stats["sigma_daily"].fillna(fam_stats["mae"] * 1.25)
    save_df(fam_stats, "family_stats")

    # Sample scatter Aktual vs Prediksi (2.000 titik representatif)
    scatter_sample = va_df.sample(n=min(2000, len(va_df)), random_state=SEED)[["y", "pred_log", "family", "store_nbr"]].rename(
        columns={"y": "actual_log"}
    )
    save_df(scatter_sample, "val_scatter")

    # Feature importance
    imp = pd.Series(m_tuned.booster_.feature_importance(importance_type="gain"), index=FITUR).sort_values(ascending=False)
    imp_pct = imp / imp.sum() * 100.0
    fi_df = pd.DataFrame({"fitur": imp_pct.index, "kontribusi_pct": imp_pct.values})

    kelompok_map = {}
    for f in FITUR:
        if f.startswith(("lag_", "roll_", "dow_mean", "selisih", "zero_share")):
            kelompok_map[f] = "Lag & rolling penjualan"
        elif f in ("store_nbr", "family", "tipe_toko", "city", "state", "cluster"):
            kelompok_map[f] = "Identitas toko/kategori"
        elif f == "onpromotion":
            kelompok_map[f] = "Promosi"
        elif f.startswith(("oil_", "trans_")):
            kelompok_map[f] = "Ekonomi & transaksi"
        elif f.startswith(("libur", "event", "hari_kerja", "pasca_gempa")):
            kelompok_map[f] = "Libur & gempa"
        else:
            kelompok_map[f] = "Kalender & gajian"
    fi_df["kelompok"] = fi_df["fitur"].map(kelompok_map)
    save_df(fi_df, "feature_importance")

    # ------------------------------------------------------------------
    # 4. Latih Ulang Model Final di Seluruh Data & Prediksi 16 Hari Test
    # ------------------------------------------------------------------
    print("Melatih ulang LightGBM (tuned) pada seluruh data train...")
    t_f = time.time()
    Xa, ya = df_model.loc[all_tr_mask, FITUR], df_model.loc[all_tr_mask, "y"]
    model_final = lgb.LGBMRegressor(**best_params)
    model_final.fit(Xa, ya)
    dt_final = time.time() - t_f
    print(f"Model final dilatih pada {len(Xa):,} baris dalam {dt_final:.1f} dtk")

    X_test = df_model.loc[te_mask, FITUR]
    pred_test = np.expm1(np.clip(model_final.predict(X_test), 0, None))

    forecast_df = df_model.loc[
        te_mask,
        ["id", "date", "store_nbr", "family", "onpromotion", "is_payday", "akhir_pekan", "libur_nasional", "libur_regional", "libur_lokal"],
    ].copy()
    forecast_df["id"] = forecast_df["id"].astype("int32")
    forecast_df["store_nbr"] = forecast_df["store_nbr"].astype("int16")
    forecast_df["family"] = forecast_df["family"].astype(str)
    forecast_df["sales_pred"] = pred_test.astype("float32")
    # Interval perkiraan berdasarkan RMSLE kategori pada skala log: expm1(log1p(pred) +- 1.28 * rmsle)
    rmsle_map = fam_stats.set_index("family")["rmsle"].clip(0.15, 0.75).to_dict()
    cat_rmsle = forecast_df["family"].map(rmsle_map).fillna(0.35).values
    log_p = np.log1p(forecast_df["sales_pred"].values)
    forecast_df["pred_lower"] = np.expm1(np.clip(log_p - 1.28 * cat_rmsle, 0, None)).astype("float32")
    forecast_df["pred_upper"] = np.expm1(log_p + 1.28 * cat_rmsle).astype("float32")
    forecast_df = forecast_df.sort_values(["date", "store_nbr", "family"]).reset_index(drop=True)
    save_df(forecast_df, "forecast_16d")

    # Simpan test_features (agar What-If Simulator dapat menjalankan inferensi real-time LightGBM!)
    test_features = df_model.loc[te_mask, ["date", "store_nbr", "family"] + FITUR].copy()
    test_features["store_nbr"] = test_features["store_nbr"].astype("int16")
    test_features["family"] = test_features["family"].astype(str)
    for col in ["tipe_toko", "city", "state"]:
        test_features[col] = test_features[col].astype(str)
    save_df(test_features, "test_features")

    # Histori 90 hari terakhir
    hist = df_model.loc[
        (~df_model["is_test"]) & (df_model["date"] > TRAIN_END - pd.Timedelta(days=90)),
        ["date", "store_nbr", "family", "sales", "onpromotion"],
    ].copy()
    hist["store_nbr"] = hist["store_nbr"].astype("int16")
    hist["family"] = hist["family"].astype(str)
    save_df(hist, "histori_90d")

    # Simpan model final (kompresi level 3 agar ukuran ramping untuk GitHub & Docker)
    joblib.dump(model_final, ART_DIR / "model_final.joblib", compress=3)

    # Ringkasan JSON metadata
    metrics_payload = {
        "train_rows": int(len(Xa)),
        "val_days": int(VAL_DAYS),
        "train_start": START_DATE,
        "train_end": str(TRAIN_END.date()),
        "forecast_start": str(forecast_df["date"].min().date()),
        "forecast_end": str(forecast_df["date"].max().date()),
        "forecast_days": int(forecast_df["date"].nunique()),
        "n_stores": int(len(TOKO)),
        "n_families": int(len(FAMILY)),
        "best_model": "LightGBM (tuned)",
        "best_params": best_params,
        "features_num": FITUR_NUM,
        "features_cat": FITUR_CAT,
        "leaderboard": lb_df.to_dict(orient="records"),
    }
    with open(ART_DIR / "model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)

    print(f"\nSemua artefak selesai diekspor dalam {time.time() - t0:.1f} detik!")
    for p in sorted(ART_DIR.iterdir()):
        print(f"  - {p.name:28s} {p.stat().st_size / 1024:8.1f} KB")


if __name__ == "__main__":
    main()
