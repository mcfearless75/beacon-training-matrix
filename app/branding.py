"""Shared branding helpers: CSS, header, KPI tiles."""
from pathlib import Path

import streamlit as st

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

BRAND_CSS = """
<style>
  /* Hide Streamlit chrome we don't want in a client demo */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header[data-testid="stHeader"] {background: transparent;}

  /* Tighten default padding so content has more breathing room */
  .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1280px;}

  /* Brand header bar */
  .brand-header {
    display: flex; align-items: center; gap: 16px;
    padding: 18px 24px; margin: -1.5rem -1rem 1.5rem -1rem;
    background: linear-gradient(135deg, #0E5FFF 0%, #0A3FB5 100%);
    border-radius: 0 0 18px 18px;
    color: white;
    box-shadow: 0 4px 18px rgba(14,95,255,0.18);
  }
  .brand-header h1 {color: white; margin: 0; font-size: 1.5rem; letter-spacing: -0.01em;}
  .brand-header .tagline {opacity: 0.85; font-size: 0.9rem; margin-top: 2px;}

  /* KPI tile */
  .kpi-grid {display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px;}
  .kpi-tile {
    background: white;
    border: 1px solid #E5E9F2;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(13,27,42,0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .kpi-tile:hover {transform: translateY(-2px); box-shadow: 0 6px 18px rgba(13,27,42,0.08);}
  .kpi-tile .label {color: #5B6B85; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600;}
  .kpi-tile .value {font-size: 2.25rem; font-weight: 700; line-height: 1.1; margin-top: 6px; color: #0D1B2A;}
  .kpi-tile .sub {color: #8896AA; font-size: 0.82rem; margin-top: 4px;}

  .kpi-tile.expired {border-left: 4px solid #E63946;}
  .kpi-tile.expired .value {color: #E63946;}
  .kpi-tile.week {border-left: 4px solid #F4845F;}
  .kpi-tile.week .value {color: #F4845F;}
  .kpi-tile.month {border-left: 4px solid #F4C24F;}
  .kpi-tile.month .value {color: #C99100;}
  .kpi-tile.quarter {border-left: 4px solid #6BBF59;}
  .kpi-tile.quarter .value {color: #4A9F40;}

  /* Login card */
  .login-shell {
    max-width: 460px; margin: 6vh auto 0 auto;
    background: white; border-radius: 20px;
    border: 1px solid #E5E9F2;
    padding: 44px 40px 36px 40px;
    box-shadow: 0 14px 50px rgba(13,27,42,0.10);
    text-align: center;
  }
  .login-logo-pill {
    display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #FFF8F0 0%, #FFE9D6 100%);
    border: 1px solid #FFD9B8;
    border-radius: 999px;
    padding: 18px 36px;
    margin-bottom: 24px;
    box-shadow: 0 4px 14px rgba(244,132,95,0.18);
  }
  .login-logo-pill img {height: 56px; width: auto; display: block;}
  .login-shell h1 {font-size: 1.75rem; margin-bottom: 6px; color: #0D1B2A; text-align: center;}
  .login-shell .login-tag {color: #5B6B85; margin-bottom: 28px; font-size: 0.95rem; text-align: center;}
  .login-shell .stTextInput input {text-align: center;}

  /* Buttons */
  .stButton > button {
    background: #0E5FFF; color: white; border: none;
    border-radius: 10px; padding: 0.6rem 1.4rem;
    font-weight: 600; font-size: 0.95rem;
    transition: background 0.15s ease, transform 0.05s ease;
  }
  .stButton > button:hover {background: #0A3FB5; color: white;}
  .stButton > button:active {transform: translateY(1px);}

  /* Dataframe + tables look cleaner */
  [data-testid="stDataFrame"] {border-radius: 10px; overflow: hidden;}

  /* Sidebar branding */
  [data-testid="stSidebar"] {background: #F4F6FA; border-right: 1px solid #E5E9F2;}
  [data-testid="stSidebar"] h1 {font-size: 1.05rem; color: #0D1B2A;}

  /* ===== Responsive: tablet ===== */
  @media (max-width: 900px) {
    .block-container {padding-left: 0.75rem; padding-right: 0.75rem;}
    .brand-header {padding: 14px 18px; border-radius: 0 0 14px 14px;}
    .brand-header h1 {font-size: 1.25rem;}
    .brand-header .tagline {font-size: 0.82rem;}
    .kpi-grid {grid-template-columns: repeat(2, 1fr); gap: 10px;}
    .kpi-tile {padding: 14px 16px;}
    .kpi-tile .value {font-size: 1.85rem;}
    .login-shell {margin: 4vh 12px 0 12px; padding: 32px 24px 28px 24px;}
    .login-logo-pill {padding: 14px 28px;}
    .login-logo-pill img {height: 44px;}
    .login-shell h1 {font-size: 1.4rem;}
  }

  /* ===== Responsive: mobile ===== */
  @media (max-width: 600px) {
    .block-container {padding-top: 1rem;}
    .brand-header {padding: 12px 14px;}
    .brand-header h1 {font-size: 1.1rem; letter-spacing: 0;}
    .brand-header .tagline {font-size: 0.75rem;}
    .kpi-grid {grid-template-columns: 1fr; gap: 8px;}
    .kpi-tile {padding: 12px 14px;}
    .kpi-tile .label {font-size: 0.7rem;}
    .kpi-tile .value {font-size: 1.65rem;}
    .kpi-tile .sub {font-size: 0.75rem;}
    .login-shell {margin: 2vh 10px 0 10px; padding: 28px 20px 24px 20px; border-radius: 16px;}
    .login-logo-pill {padding: 12px 24px;}
    .login-logo-pill img {height: 38px;}
    .login-shell h1 {font-size: 1.25rem;}
    .login-shell .login-tag {font-size: 0.85rem; margin-bottom: 20px;}
    /* Make dataframes scroll horizontally on mobile rather than squashing */
    [data-testid="stDataFrame"] > div {overflow-x: auto;}
  }

  /* Make the Matrix/dataframe area horizontally scrollable on small viewports */
  [data-testid="stDataFrame"] {max-width: 100%;}
</style>
"""


def inject_css() -> None:
    st.markdown(BRAND_CSS, unsafe_allow_html=True)


def page_header(title: str, tagline: str = "") -> None:
    st.markdown(
        f"""
        <div class="brand-header">
          <div style="flex:1;">
            <h1>{title}</h1>
            {f'<div class="tagline">{tagline}</div>' if tagline else ''}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(items: list[dict]) -> None:
    """items: [{label, value, sub, tone}] — tone in (expired|week|month|quarter)."""
    tiles = "".join(
        f"""
        <div class="kpi-tile {it.get('tone','')}">
          <div class="label">{it['label']}</div>
          <div class="value">{it['value']}</div>
          <div class="sub">{it.get('sub','')}</div>
        </div>
        """
        for it in items
    )
    st.markdown(f'<div class="kpi-grid">{tiles}</div>', unsafe_allow_html=True)
