# -*- coding: utf-8 -*-
"""Reusable dark-themed Plotly charts matching the FigCraft Dark Analytics UI."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.styles import PALETTE

BASE_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E2E8F0", size=12),
    margin=dict(l=14, r=14, t=26, b=14),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1A2440", bordercolor="#33415F", font_size=12, font_color="#F1F5F9"),
    xaxis=dict(gridcolor="rgba(37, 49, 77, 0.45)", zeroline=False, showline=False),
    yaxis=dict(gridcolor="rgba(37, 49, 77, 0.45)", zeroline=False, showline=False),
)


def _apply_base(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(**BASE_LAYOUT, height=height)
    return fig


def plot_national_trend(hist_daily: pd.DataFrame, fc_daily: pd.DataFrame, height: int = 350) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=hist_daily["date"],
            y=hist_daily["sales"],
            name="Histori aktual",
            mode="lines",
            line=dict(color=PALETTE["primary"], width=2.4),
            fill="tozeroy",
            fillcolor="rgba(99, 102, 241, 0.14)",
            hovertemplate="%{y:,.0f} unit<extra>Histori</extra>",
        )
    )
    if len(hist_daily) and len(fc_daily):
        bridge_x = pd.concat([hist_daily["date"].iloc[-1:], fc_daily["date"]])
        bridge_y = pd.concat([hist_daily["sales"].iloc[-1:], fc_daily["sales_pred"]])
        fig.add_trace(
            go.Scatter(
                x=bridge_x,
                y=bridge_y,
                name="Forecast 16 hari",
                mode="lines+markers",
                line=dict(color=PALETTE["cyan"], width=2.8, dash="dash"),
                marker=dict(size=5, color=PALETTE["bg"], line=dict(color=PALETTE["cyan"], width=2)),
                hovertemplate="%{y:,.0f} unit<extra>Forecast</extra>",
            )
        )
        split_dt = hist_daily["date"].iloc[-1]
        fig.add_vrect(
            x0=split_dt,
            x1=fc_daily["date"].iloc[-1],
            fillcolor="rgba(34, 211, 238, 0.06)",
            line_width=0,
        )
        fig.add_vline(x=split_dt, line_width=1.5, line_color="rgba(34, 211, 238, 0.65)")
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Total penjualan (unit)",
    )
    return _apply_base(fig, height=height)


def plot_explorer_series(
    hist_df: pd.DataFrame,
    fc_df: pd.DataFrame,
    show_interval: bool = True,
    height: int = 390,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=hist_df["date"],
            y=hist_df["sales"],
            name="Histori aktual",
            mode="lines",
            line=dict(color=PALETTE["primary"], width=2.4),
            fill="tozeroy",
            fillcolor="rgba(99, 102, 241, 0.12)",
            hovertemplate="%{y:,.1f} unit<extra>Histori</extra>",
        )
    )
    if len(hist_df) and len(fc_df):
        if show_interval:
            fig.add_trace(
                go.Scatter(
                    x=pd.concat([fc_df["date"], fc_df["date"][::-1]]),
                    y=pd.concat([fc_df["pred_upper"], fc_df["pred_lower"][::-1]]),
                    fill="toself",
                    fillcolor="rgba(34, 211, 238, 0.18)",
                    line=dict(color="rgba(0,0,0,0)"),
                    hoverinfo="skip",
                    name="Pita interval wajar",
                )
            )
        bridge_x = pd.concat([hist_df["date"].iloc[-1:], fc_df["date"]])
        bridge_y = pd.concat([hist_df["sales"].iloc[-1:], fc_df["sales_pred"]])
        fig.add_trace(
            go.Scatter(
                x=bridge_x,
                y=bridge_y,
                name="Forecast",
                mode="lines+markers",
                line=dict(color=PALETTE["cyan"], width=2.8, dash="dash"),
                marker=dict(size=6, color=PALETTE["bg"], line=dict(color=PALETTE["cyan"], width=2)),
                hovertemplate="%{y:,.1f} unit<extra>Forecast</extra>",
            )
        )
        pay_fc = fc_df[fc_df["is_payday"] == 1]
        if len(pay_fc):
            fig.add_trace(
                go.Scatter(
                    x=pay_fc["date"],
                    y=pay_fc["sales_pred"],
                    mode="markers",
                    name="Hari gajian",
                    marker=dict(size=10, color=PALETTE["amber"], symbol="diamond", line=dict(color="#0B1120", width=1.5)),
                    hovertemplate="Hari Gajian: %{y:,.1f} unit<extra></extra>",
                )
            )
        split_dt = hist_df["date"].iloc[-1]
        fig.add_vline(x=split_dt, line_width=1.5, line_color="rgba(34, 211, 238, 0.65)")
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Penjualan harian (unit)",
    )
    return _apply_base(fig, height=height)


def plot_whatif_comparison(df: pd.DataFrame, show_baseline: bool = True, height: int = 350) -> go.Figure:
    fig = go.Figure()
    if show_baseline:
        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df["baseline_pred"],
                name="Baseline",
                marker_color=PALETTE["primary"],
                hovertemplate="%{y:,.1f} unit<extra>Baseline</extra>",
            )
        )
    fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["scenario_pred"],
            name="Skenario",
            marker_color=PALETTE["pink"],
            hovertemplate="%{y:,.1f} unit<extra>Skenario</extra>",
        )
    )
    fig.update_layout(
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Prediksi unit / hari",
    )
    return _apply_base(fig, height=height)


def plot_horizontal_bars(labels, values, colors=None, unit_suffix: str = "", height: int = 320) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=list(values)[::-1],
            y=list(labels)[::-1],
            orientation="h",
            marker=dict(color=(list(colors)[::-1] if colors else PALETTE["primary"]), cornerradius=6),
            text=[f"{v:,.2f}{unit_suffix}" for v in list(values)[::-1]],
            textposition="outside",
            hovertemplate="%{y}: %{x:,.2f}" + unit_suffix + "<extra></extra>",
        )
    )
    fig.update_layout(showlegend=False, margin=dict(l=14, r=48, t=16, b=14))
    return _apply_base(fig, height=height)


def plot_dow_index(dow_df: pd.DataFrame, height: int = 330) -> go.Figure:
    colors = [PALETTE["pink"] if d >= 5 else PALETTE["primary"] for d in dow_df["dow"]]
    fig = go.Figure(
        go.Bar(
            x=dow_df["hari"],
            y=dow_df["indeks"],
            marker=dict(color=colors, cornerradius=6),
            text=[f"{v:.0f}" for v in dow_df["indeks"]],
            textposition="outside",
            hovertemplate="%{x}: Indeks %{y:.1f}<extra></extra>",
        )
    )
    fig.add_hline(y=100, line_dash="dot", line_color="#64748B")
    fig.update_layout(yaxis_title="Indeks (Senin = 100)")
    return _apply_base(fig, height=height)


def plot_monthly_trend(monthly_df: pd.DataFrame, height: int = 330) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=monthly_df["year_month"],
            y=monthly_df["sales"] / 1e6,
            mode="lines",
            line=dict(color=PALETTE["violet"], width=2.5),
            fill="tozeroy",
            fillcolor="rgba(139, 92, 246, 0.16)",
            name="Total bulanan",
            hovertemplate="%{x|%b %Y}: %{y:.2f} Jt unit<extra></extra>",
        )
    )
    dec = monthly_df[monthly_df["year_month"].dt.month == 12]
    fig.add_trace(
        go.Scatter(
            x=dec["year_month"],
            y=dec["sales"] / 1e6,
            mode="markers",
            marker=dict(size=9, color=PALETTE["amber"], symbol="star"),
            name="Puncak Desember",
            hovertemplate="Des %{x|%Y}: %{y:.2f} Jt unit<extra></extra>",
        )
    )
    fig.update_layout(yaxis_title="Juta unit / bulan", legend=dict(orientation="h", y=1.08, x=1, xanchor="right"))
    return _apply_base(fig, height=height)


def plot_earthquake_window(daily_df: pd.DataFrame, height: int = 320) -> go.Figure:
    win = daily_df[(daily_df["date"] >= "2016-03-01") & (daily_df["date"] <= "2016-06-15")].copy()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=win["date"],
            y=win["sales"] / 1e3,
            name="Sales harian (ribu)",
            line=dict(color=PALETTE["red"], width=2.2),
            hovertemplate="%{y:,.0f} rb unit<extra>Sales</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=win["date"],
            y=win["tren_29"] / 1e3,
            name="Tren 29 hari",
            line=dict(color="#94A3B8", width=1.8, dash="dash"),
            hovertemplate="%{y:,.0f} rb unit<extra>Tren</extra>",
        )
    )
    gempa = pd.Timestamp("2016-04-16")
    fig.add_vline(x=gempa, line_color=PALETTE["red"], line_width=2)
    fig.add_annotation(
        x=gempa,
        y=win["sales"].max() / 1e3,
        text="Gempa M7,8 (16 Apr 2016)",
        showarrow=True,
        arrowhead=2,
        bgcolor="#7F1D1D",
        font=dict(color="#FFFFFF", size=11),
    )
    fig.update_layout(yaxis_title="Ribu unit / hari", legend=dict(orientation="h", y=1.08, x=1, xanchor="right"))
    return _apply_base(fig, height=height)


def plot_oil_vs_sales(monthly_df: pd.DataFrame, height: int = 320) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=monthly_df["year_month"],
            y=monthly_df["oil_price"],
            name="Harga minyak WTI (USD)",
            line=dict(color=PALETTE["amber"], width=2.4),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_df["year_month"],
            y=monthly_df["sales"] / 1e6,
            name="Penjualan (Jt unit)",
            line=dict(color=PALETTE["violet"], width=2.2, dash="dash"),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Harga WTI (USD)", secondary_y=False, gridcolor="rgba(37, 49, 77, 0.45)")
    fig.update_yaxes(title_text="Penjualan (Jt unit)", secondary_y=True, showgrid=False)
    fig.update_layout(legend=dict(orientation="h", y=1.1, x=1, xanchor="right"))
    return _apply_base(fig, height=height)


def plot_pareto(pareto_df: pd.DataFrame, top_n: int = 12, height: int = 340) -> go.Figure:
    top = pareto_df.head(top_n).copy()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    cols = [PALETTE["primary"] if i < 5 else "#33415F" for i in range(len(top))]
    fig.add_trace(
        go.Bar(
            x=top["family"],
            y=top["share_pct"],
            name="Pangsa (%)",
            marker=dict(color=cols, cornerradius=5),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=top["family"],
            y=top["cum_share_pct"],
            name="Kumulatif (%)",
            mode="lines+markers",
            line=dict(color=PALETTE["cyan"], width=2.5),
            marker=dict(size=6),
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Pangsa (%)", secondary_y=False, gridcolor="rgba(37, 49, 77, 0.45)")
    fig.update_yaxes(title_text="Kumulatif (%)", secondary_y=True, range=[0, 105], showgrid=False)
    fig.update_layout(legend=dict(orientation="h", y=1.1, x=1, xanchor="right"))
    return _apply_base(fig, height=height)


def plot_actual_vs_pred(scatter_df: pd.DataFrame, height: int = 330) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scattergl(
            x=scatter_df["actual_log"],
            y=scatter_df["pred_log"],
            mode="markers",
            marker=dict(size=5, color=PALETTE["cyan"], opacity=0.55),
            name="Sampel validasi",
            text=scatter_df["family"],
            hovertemplate="Aktual: %{x:.2f} | Prediksi: %{y:.2f}<br>%{text}<extra></extra>",
        )
    )
    lo = float(min(scatter_df["actual_log"].min(), scatter_df["pred_log"].min()))
    hi = float(max(scatter_df["actual_log"].max(), scatter_df["pred_log"].max()))
    fig.add_trace(
        go.Scatter(
            x=[lo, hi],
            y=[lo, hi],
            mode="lines",
            line=dict(color=PALETTE["red"], width=1.8, dash="dash"),
            name="Garis ideal (y = x)",
        )
    )
    fig.update_layout(
        hovermode="closest",
        xaxis_title="Aktual log1p(sales)",
        yaxis_title="Prediksi log1p(sales)",
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right"),
    )
    return _apply_base(fig, height=height)


def plot_overfitting_check(lb_df: pd.DataFrame, height: int = 330) -> go.Figure:
    sub = lb_df.dropna(subset=["RMSLE_train"]).copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=sub["model"], y=sub["RMSLE_train"], name="Train RMSLE", marker_color=PALETTE["violet"]))
    fig.add_trace(go.Bar(x=sub["model"], y=sub["RMSLE"], name="Validasi RMSLE", marker_color=PALETTE["cyan"]))
    fig.update_layout(
        barmode="group",
        yaxis_title="RMSLE (makin kecil makin baik)",
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right"),
    )
    return _apply_base(fig, height=height)
