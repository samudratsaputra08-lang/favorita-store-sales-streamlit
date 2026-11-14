# -*- coding: utf-8 -*-
"""
Favorita Store Sales Forecasting App
Mini Project Data Science & Generative AI — Kelompok 7 (Celerates)
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Favorita Forecast · Store Sales AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.data_loader import render_sidebar_filters
from utils.styles import inject_global_css
from utils.tour import init_tour_state, render_onboarding_screen
from views.eda import render_eda
from views.explorer import render_explorer
from views.guide import render_guide
from views.home import render_home
from views.model_perf import render_model_perf
from views.simulator import render_simulator

inject_global_css()
init_tour_state()

PAGES = [
    ("home", "🏠  Beranda", render_home),
    ("explorer", "📈  Forecast Explorer", render_explorer),
    ("simulator", "🧪  Simulasi What-If", render_simulator),
    ("eda", "📊  Insight EDA", render_eda),
    ("model", "⚙️  Performa Model", render_model_perf),
    ("guide", "📘  Panduan & Bantuan", render_guide),
]
PAGE_KEYS = [p[0] for p in PAGES]
PAGE_LABELS = {p[0]: p[1] for p in PAGES}
PAGE_FUNCS = {p[0]: p[2] for p in PAGES}

if "nav_target" not in st.session_state:
    st.session_state["nav_target"] = "home"

# Sidebar Brand
st.sidebar.markdown(
    """
    <div class="fc-brand">
        <div class="fc-brand-icon">📈</div>
        <div>
            <div class="fc-brand-title">Favorita Forecast</div>
            <div class="fc-brand-sub">Store Sales AI · Kelompok 7</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    '<div style="font-size:11px;font-weight:700;color:#64748B;letter-spacing:0.08em;margin-bottom:6px;">NAVIGASI</div>',
    unsafe_allow_html=True,
)

# Navigation radio synchronized with programmatic nav_target jumps
selected_key = st.sidebar.radio(
    "Navigasi",
    options=PAGE_KEYS,
    index=PAGE_KEYS.index(st.session_state["nav_target"]),
    format_func=lambda k: PAGE_LABELS[k],
    label_visibility="collapsed",
)
if selected_key != st.session_state["nav_target"]:
    st.session_state["nav_target"] = selected_key
    st.rerun()

filters = render_sidebar_filters()

if not render_onboarding_screen():
    PAGE_FUNCS[st.session_state["nav_target"]](filters)
