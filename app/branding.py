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

  /* Global font upgrade */
  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }

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

  /* ===== Login experience ===== */
  /* Atmospheric background applied to the whole app on login page */
  .login-active {
    background:
      radial-gradient(1200px 600px at 80% -10%, rgba(244,132,95,0.18), transparent 60%),
      radial-gradient(900px 500px at 10% 110%, rgba(14,95,255,0.10), transparent 60%),
      linear-gradient(180deg, #FFFBF6 0%, #F7F4EF 100%) !important;
    min-height: 100vh;
  }
  .login-active [data-testid="stAppViewContainer"] {background: transparent !important;}
  .login-active .block-container {max-width: 480px; padding-top: 4vh;}

  /* Card top — logo + headings */
  .login-shell {
    background: linear-gradient(180deg, #FFFFFF 0%, #FFFCF8 100%);
    border-radius: 24px 24px 0 0;
    border: 1px solid #F1E4D2;
    border-bottom: none;
    padding: 40px 36px 24px 36px;
    text-align: center;
    box-shadow: 0 24px 60px -20px rgba(244,132,95,0.22), 0 8px 24px rgba(13,27,42,0.06);
    position: relative;
  }
  /* Decorative top accent line */
  .login-shell::before {
    content: ""; position: absolute; top: 0; left: 24px; right: 24px; height: 3px;
    background: linear-gradient(90deg, #F4845F, #FFB74D, #F4845F);
    border-radius: 0 0 6px 6px;
  }
  .login-logo-pill {
    display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #FFF8F0 0%, #FFE2C6 100%);
    border: 1px solid #FFD3AC;
    border-radius: 999px;
    padding: 18px 36px;
    margin-bottom: 22px;
    box-shadow: 0 6px 20px rgba(244,132,95,0.22), inset 0 -2px 0 rgba(255,255,255,0.6);
  }
  .login-logo-pill img {height: 56px; width: auto; display: block;}
  .login-shell h1 {
    font-size: 1.85rem; margin-bottom: 8px; color: #0D1B2A;
    letter-spacing: -0.02em; font-weight: 700; text-align: center;
  }
  .login-shell .login-tag {
    color: #6B7B95; margin-bottom: 4px; font-size: 0.95rem; text-align: center;
  }

  /* Card body — Streamlit inputs/buttons styled to extend the card */
  .login-active [data-testid="stTextInput"] {
    margin-top: 0 !important;
    background: white;
    border-left: 1px solid #F1E4D2;
    border-right: 1px solid #F1E4D2;
    padding: 8px 32px 0 32px;
  }
  .login-active [data-testid="stTextInput"] > div > div > input {
    text-align: center;
    background: #FAFBFD !important;
    border: 1px solid #E5E9F2 !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    font-size: 1rem !important;
    font-weight: 500;
    letter-spacing: 0.02em;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
  }
  .login-active [data-testid="stTextInput"] > div > div > input:focus {
    border-color: #F4845F !important;
    box-shadow: 0 0 0 3px rgba(244,132,95,0.18) !important;
  }

  /* Primary buttons inside the login experience — bold orange gradient */
  .login-active [data-testid="stVerticalBlock"] > div:has(> .stButton),
  .login-active [data-testid="stHorizontalBlock"] {
    background: white;
    border-left: 1px solid #F1E4D2;
    border-right: 1px solid #F1E4D2;
    padding: 14px 32px 8px 32px;
  }
  .login-active .stButton > button {
    background: linear-gradient(135deg, #F4845F 0%, #E5663C 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.98rem !important;
    letter-spacing: 0.01em;
    box-shadow: 0 4px 14px rgba(244,132,95,0.32), inset 0 -2px 0 rgba(0,0,0,0.06) !important;
    transition: transform 0.08s ease, box-shadow 0.15s ease, filter 0.15s ease !important;
  }
  .login-active .stButton > button:hover {
    filter: brightness(1.05);
    box-shadow: 0 6px 18px rgba(244,132,95,0.42), inset 0 -2px 0 rgba(0,0,0,0.08) !important;
  }
  .login-active .stButton > button:active {transform: translateY(1px);}

  /* Secondary "Use different email" — subtle */
  .login-active [data-testid="column"]:last-child .stButton > button {
    background: white !important; color: #5B6B85 !important;
    border: 1px solid #E5E9F2 !important;
    box-shadow: none !important;
    font-weight: 500 !important;
  }
  .login-active [data-testid="column"]:last-child .stButton > button:hover {
    background: #F4F6FA !important;
  }

  /* Info / success / error blocks while logged out — softer rounded edges */
  .login-active [data-testid="stAlert"] {
    margin-left: 32px; margin-right: 32px;
    border-radius: 12px;
    background: white;
    border-left: 1px solid #F1E4D2 !important;
    border-right: 1px solid #F1E4D2 !important;
  }

  /* Card bottom — footer caption */
  .login-footer {
    background: linear-gradient(180deg, #FFFCF8 0%, #FFF6EC 100%);
    border-radius: 0 0 24px 24px;
    border: 1px solid #F1E4D2;
    border-top: none;
    padding: 16px 32px 22px 32px;
    text-align: center;
    color: #8C7B66;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 600;
  }
  .login-footer .dot {color: #F4845F; margin: 0 8px;}

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
