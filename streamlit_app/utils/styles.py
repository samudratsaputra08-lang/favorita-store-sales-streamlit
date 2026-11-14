# -*- coding: utf-8 -*-
"""Custom Dark Analytics styling matching the FigCraft UI/UX design."""
from __future__ import annotations

import streamlit as st

PALETTE = {
    "bg": "#0B1120",
    "side": "#0E1528",
    "card": "#131C31",
    "card2": "#1A2440",
    "border": "#25314D",
    "border2": "#33415F",
    "text": "#F1F5F9",
    "muted": "#94A3B8",
    "dim": "#64748B",
    "primary": "#6366F1",
    "violet": "#8B5CF6",
    "cyan": "#22D3EE",
    "green": "#10B981",
    "amber": "#F59E0B",
    "red": "#F43F5E",
    "pink": "#EC4899",
    "sky": "#38BDF8",
}


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .stApp {
            background-color: #0B1120;
            color: #F1F5F9;
        }

        section[data-testid="stSidebar"] {
            background-color: #0E1528;
            border-right: 1px solid #25314D;
        }

        .block-container {
            padding-top: 1.75rem;
            padding-bottom: 3rem;
            max-width: 1320px;
        }

        /* Sidebar brand header */
        .fc-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 4px 0 14px 0;
            margin-bottom: 10px;
            border-bottom: 1px solid #25314D;
        }
        .fc-brand-icon {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, #6366F1, #8B5CF6);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
            flex-shrink: 0;
        }
        .fc-brand-title {
            font-size: 16px;
            font-weight: 700;
            color: #F1F5F9;
            line-height: 1.2;
        }
        .fc-brand-sub {
            font-size: 11px;
            color: #64748B;
            margin-top: 2px;
        }

        /* Hero Banner */
        .fc-hero {
            background: linear-gradient(125deg, #4338CA 0%, #7C3AED 55%, #DB2777 100%);
            border-radius: 20px;
            padding: 24px 28px;
            margin-bottom: 20px;
            box-shadow: 0 12px 32px rgba(99, 102, 241, 0.25);
            position: relative;
            overflow: hidden;
        }
        .fc-hero h2 {
            color: #FFFFFF !important;
            margin: 0 0 8px 0 !important;
            font-size: 22px !important;
            font-weight: 700 !important;
        }
        .fc-hero p {
            color: #E0E7FF;
            margin: 0;
            font-size: 14px;
            line-height: 1.55;
            max-width: 820px;
        }

        /* Champion Banner */
        .fc-champion {
            background: linear-gradient(120deg, #064E3B 0%, #0E7490 100%);
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: 20px;
            padding: 22px 26px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        .fc-champion-title {
            font-size: 20px;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 4px;
        }
        .fc-champion-sub {
            font-size: 13px;
            color: #A7F3D0;
        }
        .fc-champion-stats {
            display: flex;
            gap: 28px;
        }
        .fc-champion-stat-val {
            font-size: 22px;
            font-weight: 700;
            color: #FFFFFF;
            text-align: center;
        }
        .fc-champion-stat-lbl {
            font-size: 11px;
            color: #A7F3D0;
            text-align: center;
        }

        /* KPI Card */
        .fc-kpi {
            background: #131C31;
            border: 1px solid #25314D;
            border-radius: 16px;
            padding: 18px 20px;
            height: 100%;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        }
        .fc-kpi-top {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        .fc-kpi-icon {
            width: 38px;
            height: 38px;
            border-radius: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }
        .fc-kpi-label {
            font-size: 12px;
            font-weight: 600;
            color: #94A3B8;
            line-height: 1.25;
        }
        .fc-kpi-foot {
            font-size: 11px;
            color: #64748B;
            margin-top: 2px;
        }
        .fc-kpi-value {
            font-size: 26px;
            font-weight: 800;
            color: #F1F5F9;
            line-height: 1.15;
            margin-bottom: 8px;
        }
        .fc-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
        }

        /* Generic dark card */
        .fc-card {
            background: #131C31;
            border: 1px solid #25314D;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
        }
        .fc-card-title {
            font-size: 15px;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 4px;
        }
        .fc-card-sub {
            font-size: 12px;
            color: #94A3B8;
            margin-bottom: 14px;
        }

        /* Insight box */
        .fc-insight {
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }
        .fc-insight-title {
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 2px;
        }
        .fc-insight-body {
            font-size: 12px;
            color: #CBD5E1;
            line-height: 1.45;
        }

        /* Sidebar Help Card */
        .fc-help-card {
            background: linear-gradient(135deg, #4338CA 0%, #7C3AED 55%, #DB2777 100%);
            border-radius: 16px;
            padding: 16px;
            margin-top: 12px;
            color: #FFFFFF;
        }
        .fc-help-card h4 {
            margin: 0 0 6px 0 !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }
        .fc-help-card p {
            margin: 0;
            font-size: 12px;
            color: #E0E7FF;
            line-height: 1.45;
        }

        /* Coach-mark tour box */
        .fc-tour-box {
            background: #FFFFFF;
            color: #0F172A;
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 18px;
            box-shadow: 0 12px 32px rgba(99, 102, 241, 0.32);
            border: 2px solid #22D3EE;
        }
        .fc-tour-step {
            display: inline-block;
            background: rgba(99, 102, 241, 0.14);
            color: #4F46E5;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 999px;
            margin-bottom: 8px;
        }
        .fc-tour-title {
            font-size: 17px;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 4px;
        }
        .fc-tour-desc {
            font-size: 13px;
            color: #475569;
            line-height: 1.5;
        }

        /* Formula box */
        .fc-formula {
            background: #0D1426;
            border: 1px solid #33415F;
            border-radius: 12px;
            padding: 14px 16px;
            text-align: center;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 20px;
            font-weight: 700;
            color: #22D3EE;
            margin: 8px 0 12px 0;
        }

        /* Quick start step card */
        .fc-qstep {
            background: #131C31;
            border: 1px solid #25314D;
            border-radius: 14px;
            padding: 16px;
            height: 100%;
        }
        .fc-qnum {
            width: 32px;
            height: 32px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 14px;
            margin-bottom: 10px;
        }

        /* Status dot footer */
        .fc-status-footer {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            color: #64748B;
            margin-top: 14px;
            padding-top: 10px;
            border-top: 1px solid #25314D;
        }
        .fc-dot-green {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #10B981;
            display: inline-block;
            flex-shrink: 0;
        }

        /* Streamlit native elements polish */
        div[data-testid="stMetric"] {
            background-color: #131C31;
            border: 1px solid #25314D;
            padding: 14px 18px;
            border-radius: 14px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid #25314D;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
            color: #94A3B8;
        }
        .stTabs [aria-selected="true"] {
            color: #F1F5F9 !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    emoji: str,
    color: str,
    label: str,
    value: str,
    delta: str | None = None,
    delta_color: str = "#10B981",
    foot: str = "",
) -> str:
    badge_html = (
        f'<span class="fc-badge" style="background:{delta_color}24;color:{delta_color};">{delta}</span>'
        if delta
        else ""
    )
    foot_html = f'<div class="fc-kpi-foot">{foot}</div>' if foot else ""
    return f"""
    <div class="fc-kpi">
        <div class="fc-kpi-top">
            <div class="fc-kpi-icon" style="background:{color}26;">{emoji}</div>
            <div>
                <div class="fc-kpi-label">{label}</div>
                {foot_html}
            </div>
        </div>
        <div class="fc-kpi-value">{value}</div>
        {badge_html}
    </div>
    """


def render_page_header(breadcrumb: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div style="font-size:12px;font-weight:600;color:#64748B;margin-bottom:2px;">{breadcrumb}</div>'
        f'<h1 style="font-size:30px;font-weight:800;margin:0 0 6px 0;color:#F1F5F9;">{title}</h1>'
        f'<p style="font-size:14px;color:#94A3B8;margin:0 0 18px 0;max-width:780px;">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def fmt_id(val: float, decimals: int = 0) -> str:
    s = f"{val:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")
