"""Shared branding helpers: CSS, header, KPI tiles."""
from pathlib import Path

import streamlit as st

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

BRAND_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
  /* ===== 0. Streamlit chrome ===== */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header[data-testid="stHeader"] {background: transparent;}

  /* ===== 1. Design tokens ===== */
  :root {
    --or:  #E86038;
    --or2: #C94E27;
    --olt: #FEF0EA;
    --omd: #FDD5C2;
    --t0:  #0F172A;
    --t1:  #1E293B;
    --t2:  #334155;
    --mu:  #64748B;
    --su:  #94A3B8;
    --bd:  #E2E8F0;
    --bd2: #CBD5E1;
    --sf:  #FFFFFF;
    --bg:  #F4F7FC;
    --nav: #0D1526;
  }

  /* ===== 2. Base ===== */
  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }
  .block-container {padding-top: 2rem; padding-bottom: 4rem; max-width: 1280px;}
  [data-testid="stAppViewContainer"] {background: var(--bg);}
  /* Fade-in on CSS load — masks the FOUC transition so styled content appears smoothly */
  [data-testid="stAppViewContainer"] > section > div {
    animation: beacon-fadein 0.22s ease-out;
  }
  @keyframes beacon-fadein {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  /* ===== 3. Headings ===== */
  h2 {font-size: 1.2rem !important; font-weight: 700 !important; color: var(--t0) !important; letter-spacing: -0.015em !important;}
  h3 {font-size: 1rem !important; font-weight: 600 !important; color: var(--t0) !important; letter-spacing: -0.01em !important;}
  [data-testid="stMarkdownContainer"] hr {border: none !important; border-top: 1px solid var(--bd) !important; margin: 18px 0 !important;}

  /* ===== 4. Sidebar — dark navy ===== */
  [data-testid="stSidebar"] {background: var(--nav) !important; border-right: none !important;}
  [data-testid="stSidebar"] > div:first-child {padding-top: 0 !important;}

  [data-testid="stSidebarNav"] {padding: 8px 0 4px 0;}
  [data-testid="stSidebarNav"] a {
    border-radius: 8px !important; margin: 2px 10px !important;
    padding: 9px 12px !important; transition: background 0.15s;
  }
  [data-testid="stSidebarNav"] a:hover {background: rgba(255,255,255,0.08) !important;}
  [data-testid="stSidebarNav"] a span {color: #94A3B8 !important; font-weight: 500 !important; font-size: 0.88rem !important;}
  [data-testid="stSidebarNav"] a:hover span {color: #E2E8F0 !important;}
  [data-testid="stSidebarNav"] a[aria-current="page"] {background: rgba(232,96,56,0.18) !important; border: none !important; padding-left: 12px !important;}
  [data-testid="stSidebarNav"] a[aria-current="page"] span {color: #FBBF9A !important; font-weight: 600 !important;}

  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
    color: #E2E8F0 !important; font-size: 0.78rem !important;
    font-weight: 700 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important;
  }
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] .stMarkdown {color: #94A3B8 !important; font-size: 0.88rem !important;}
  [data-testid="stSidebar"] strong {color: #CBD5E1 !important; font-weight: 600 !important;}
  [data-testid="stSidebar"] hr {border-color: rgba(255,255,255,0.08) !important; margin: 10px 16px !important;}

  [data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.06) !important; color: #94A3B8 !important;
    border: 1px solid rgba(255,255,255,0.10) !important; border-radius: 8px !important;
    font-size: 0.85rem !important; font-weight: 500 !important;
    padding: 0.4rem 0.9rem !important; box-shadow: none !important;
    transition: background 0.15s, color 0.15s !important;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important; color: #E2E8F0 !important; transform: none !important;
  }

  /* ===== 5. Brand page header ===== */
  .brand-header {
    padding: 24px 4px 20px 4px; margin: 0 0 24px 0;
    border-bottom: 1px solid var(--bd); background: transparent; position: relative;
  }
  .brand-header .eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--or); margin-bottom: 8px;
  }
  .brand-header .eyebrow::before {
    content: ""; display: inline-block; width: 6px; height: 6px;
    background: var(--or); border-radius: 50%;
  }
  .brand-header h1 {color: var(--t0); margin: 0; font-size: 1.65rem; font-weight: 700; letter-spacing: -0.022em;}
  .brand-header .tagline {color: var(--mu); font-size: 0.9rem; margin-top: 6px; font-weight: 400;}

  /* KPI tiles — modern, spacious, hover lift */
  .kpi-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-bottom: 28px;
  }
  .kpi-tile {
    background: white;
    border: 1px solid var(--bd);
    border-radius: 14px;
    padding: 18px 20px 16px 20px;
    transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s, border-color 0.18s;
    position: relative; overflow: hidden;
  }
  .kpi-tile:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px -10px rgba(15, 23, 42, 0.10);
    border-color: #D8DCE3;
  }
  .kpi-tile .kpi-meta {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 10px;
  }
  .kpi-tile .label {
    color: #64748B; font-size: 0.74rem; font-weight: 600;
    letter-spacing: 0.05em; text-transform: uppercase;
  }
  .kpi-tile .value {
    font-size: 2.4rem; font-weight: 700;
    line-height: 1; color: #0F172A;
    letter-spacing: -0.03em; font-variant-numeric: tabular-nums;
  }
  .kpi-tile .sub {
    color: #94A3B8; font-size: 0.8rem;
    margin-top: 8px; font-weight: 500;
  }

  .kpi-tile [class^="dot-"] {
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  }
  .kpi-tile .dot-expired {background: #DC2626; box-shadow: 0 0 0 4px rgba(220,38,38,0.12);}
  .kpi-tile .dot-week {background: #EA580C; box-shadow: 0 0 0 4px rgba(234,88,12,0.12);}
  .kpi-tile .dot-month {background: #D97706; box-shadow: 0 0 0 4px rgba(217,119,6,0.12);}
  .kpi-tile .dot-quarter {background: #16A34A; box-shadow: 0 0 0 4px rgba(22,163,74,0.12);}

  .kpi-tile.expired .value {color: #DC2626;}
  .kpi-tile.week .value {color: #EA580C;}
  .kpi-tile.month .value {color: #D97706;}
  .kpi-tile.quarter .value {color: #16A34A;}

  /* ===== Login — clean centred card, no JS body class ===== */
  /* Card sits in the middle column — always centred, always works */
  .login-shell {
    background: var(--sf);
    border-radius: 16px;
    border: 1px solid var(--bd);
    padding: 44px 36px 28px 36px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(15,23,42,0.08), 0 1px 4px rgba(15,23,42,0.04);
    position: relative; overflow: hidden;
    margin-bottom: 6px;
  }
  /* Thin orange accent bar */
  .login-shell::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--or2) 0%, var(--or) 50%, #FFB84D 100%);
  }
  /* Logo — clean, no pill background */
  .login-logo-pill {
    display: flex; align-items: center; justify-content: center; margin-bottom: 22px;
  }
  .login-logo-pill img {height: 56px; width: auto; display: block;}
  /* Eyebrow + heading + tagline */
  .login-eyebrow {
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--or); margin-bottom: 10px;
  }
  .login-shell h1 {
    font-size: 1.85rem; margin-bottom: 10px; color: var(--t0);
    letter-spacing: -0.03em; font-weight: 800; line-height: 1.1;
  }
  .login-shell .login-tag {
    color: var(--mu); font-size: 0.9rem; line-height: 1.6; font-weight: 400; margin-bottom: 0;
  }
  .login-divider {
    height: 1px; margin: 22px 0 0 0;
    background: linear-gradient(90deg, transparent, var(--bd) 25%, var(--bd) 75%, transparent);
  }
  /* Footer — slim, centred, below card */
  .login-footer {
    text-align: center; padding: 18px 0 8px 0;
    color: var(--su); font-size: 0.72rem;
    letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600;
  }
  .login-footer .dot {color: var(--or); margin: 0 6px; opacity: 0.55;}

  /* ===== 6. Buttons (outside login) ===== */
  .stButton > button {
    background: var(--sf) !important; color: var(--t0) !important;
    border: 1px solid var(--bd) !important; border-radius: 8px !important;
    padding: 0.5rem 1.1rem !important; font-weight: 500 !important; font-size: 0.9rem !important;
    box-shadow: 0 1px 2px rgba(15,23,42,0.04) !important;
    transition: background 0.12s, border-color 0.12s, box-shadow 0.12s !important;
  }
  .stButton > button:hover {
    background: #F8FAFC !important; border-color: var(--bd2) !important;
    box-shadow: 0 2px 6px rgba(15,23,42,0.08) !important;
  }
  .stButton > button:active {transform: translateY(1px) !important;}
  .stButton > button[kind="primary"] {
    background: var(--or) !important; color: white !important;
    border-color: transparent !important; box-shadow: 0 4px 12px rgba(232,96,56,0.28) !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: var(--or2) !important; box-shadow: 0 6px 16px rgba(232,96,56,0.36) !important;
  }

  /* ===== 7. Forms ===== */
  [data-testid="stTextInput"] label, [data-testid="stTextArea"] label,
  [data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label,
  [data-testid="stNumberInput"] label, .stDateInput label, .stSlider label {
    font-size: 0.82rem !important; font-weight: 600 !important;
    color: var(--t2) !important; letter-spacing: 0.01em !important;
  }
  [data-testid="stTextInput"] input,
  [data-testid="stNumberInput"] input,
  [data-testid="stTextArea"] textarea {
    background: var(--sf) !important; border: 1.5px solid var(--bd) !important;
    border-radius: 8px !important; padding: 10px 13px !important;
    font-size: 0.9rem !important; color: var(--t0) !important;
    box-shadow: 0 1px 2px rgba(15,23,42,0.04) !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
  }
  [data-testid="stTextInput"] input:focus,
  [data-testid="stNumberInput"] input:focus,
  [data-testid="stTextArea"] textarea:focus {
    border-color: var(--or) !important; box-shadow: 0 0 0 3px rgba(232,96,56,0.12) !important;
  }
  [data-testid="stTextInput"] input::placeholder,
  [data-testid="stTextArea"] textarea::placeholder {color: #A8B3C8 !important;}
  [data-testid="stSelectbox"] > div > div {
    background: var(--sf) !important; border: 1.5px solid var(--bd) !important;
    border-radius: 8px !important; box-shadow: 0 1px 2px rgba(15,23,42,0.04) !important;
  }
  [data-testid="stSelectbox"] > div > div:focus-within {
    border-color: var(--or) !important; box-shadow: 0 0 0 3px rgba(232,96,56,0.12) !important;
  }
  [data-testid="stMultiSelect"] > div > div {
    background: var(--sf) !important; border: 1.5px solid var(--bd) !important;
    border-radius: 8px !important; box-shadow: 0 1px 2px rgba(15,23,42,0.04) !important;
  }
  [data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: var(--or) !important; box-shadow: 0 0 0 3px rgba(232,96,56,0.12) !important;
  }
  [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background: var(--olt) !important; border: 1px solid var(--omd) !important;
    color: #9A3015 !important; border-radius: 5px !important;
    font-weight: 500 !important; font-size: 0.78rem !important;
  }
  [data-testid="stFileUploaderDropzone"] {
    border: 2px dashed var(--bd2) !important; border-radius: 12px !important;
    background: var(--sf) !important; transition: border-color 0.15s, background 0.15s !important;
  }
  [data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--or) !important; background: var(--olt) !important;
  }

  /* ===== 8. Tabs ===== */
  .stTabs [data-baseweb="tab-list"] {
    background: transparent !important; gap: 2px !important;
    border-bottom: 2px solid var(--bd) !important;
    padding-bottom: 0 !important; margin-bottom: 20px !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    padding: 8px 18px !important; border-radius: 6px 6px 0 0 !important;
    color: var(--mu) !important; font-weight: 500 !important; font-size: 0.9rem !important;
    transition: color 0.15s, background 0.15s !important; margin-bottom: -2px !important;
  }
  .stTabs [data-baseweb="tab"]:hover {background: #F1F5F9 !important; color: var(--t0) !important;}
  .stTabs [aria-selected="true"][data-baseweb="tab"] {
    color: var(--or) !important; font-weight: 600 !important;
    background: transparent !important; border-bottom: 2px solid var(--or) !important;
  }
  .stTabs [data-baseweb="tab-highlight"] {background: var(--or) !important; height: 2px !important;}
  .stTabs [data-baseweb="tab-panel"] {padding: 0 !important;}

  /* ===== 9. Metrics ===== */
  [data-testid="stMetric"] {
    background: var(--sf) !important; border: 1px solid var(--bd) !important;
    border-radius: 16px !important; padding: 18px 20px !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06) !important;
    transition: box-shadow 0.18s !important;
  }
  [data-testid="stMetric"]:hover {box-shadow: 0 8px 20px -4px rgba(15,23,42,0.12) !important;}
  [data-testid="stMetricLabel"] {
    font-size: 0.74rem !important; font-weight: 600 !important;
    letter-spacing: 0.05em !important; text-transform: uppercase !important; color: var(--mu) !important;
  }
  [data-testid="stMetricValue"] {
    font-size: 2rem !important; font-weight: 700 !important;
    letter-spacing: -0.02em !important; color: var(--t0) !important;
    font-variant-numeric: tabular-nums !important;
  }

  /* ===== 10. Progress bars ===== */
  [data-testid="stProgress"] > div > div {border-radius: 999px !important; background: var(--bd) !important;}
  [data-testid="stProgress"] > div > div > div {
    background: linear-gradient(90deg, var(--or), #FBB17A) !important; border-radius: 999px !important;
  }

  /* ===== 11. Tables ===== */
  [data-testid="stDataFrame"] {
    border-radius: 12px !important; border: 1px solid var(--bd) !important;
    overflow: hidden !important; box-shadow: 0 1px 3px rgba(15,23,42,0.05) !important;
  }

  /* ===== 12. Scrollbar ===== */
  ::-webkit-scrollbar {width: 6px; height: 6px;}
  ::-webkit-scrollbar-track {background: transparent;}
  ::-webkit-scrollbar-thumb {background: #CBD5E1; border-radius: 999px;}
  ::-webkit-scrollbar-thumb:hover {background: #94A3B8;}

  /* Profile page */
  .profile-card {
    display: flex; align-items: center; gap: 20px;
    background: white; border: 1px solid var(--bd); border-radius: 16px;
    padding: 24px 28px; margin-bottom: 18px;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03);
  }
  .profile-avatar {
    width: 64px; height: 64px; border-radius: 50%;
    background: linear-gradient(135deg, #F4845F 0%, #E5663C 100%);
    color: white; display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; font-weight: 700;
    box-shadow: 0 4px 14px rgba(244,132,95,0.32);
  }
  .profile-name {font-size: 1.35rem; font-weight: 700; color: #0F172A; letter-spacing: -0.015em;}
  .profile-job {color: #475569; font-size: 0.95rem; margin-top: 2px;}
  .profile-start {color: #94A3B8; font-size: 0.82rem; margin-top: 4px;}
  .profile-stats {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
    margin-bottom: 22px;
  }
  .profile-stat {
    background: white; border: 1px solid var(--bd); border-radius: 12px;
    padding: 16px 18px;
  }
  .profile-stat .ps-value {
    font-size: 1.8rem; font-weight: 700; line-height: 1;
    letter-spacing: -0.02em; color: #0F172A;
    font-variant-numeric: tabular-nums;
  }
  .profile-stat .ps-label {
    color: #64748B; font-size: 0.78rem; font-weight: 600;
    letter-spacing: 0.04em; text-transform: uppercase; margin-top: 8px;
  }
  @media (max-width: 700px) {
    .profile-stats {grid-template-columns: repeat(2, 1fr);}
  }

  /* Timeline (renewal calendar) */
  .timeline-card {
    background: white; border: 1px solid var(--bd); border-radius: 16px;
    padding: 24px 28px 20px 28px; margin-bottom: 22px;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03);
  }
  .tl-chart {
    display: flex; gap: 6px; align-items: flex-end;
    height: 220px; padding-bottom: 8px;
    overflow-x: auto;
  }
  .tl-col {
    flex: 1 0 60px; min-width: 60px;
    display: flex; flex-direction: column; align-items: center;
    justify-content: flex-end;
    height: 100%;
  }
  .tl-count {
    font-size: 0.85rem; font-weight: 700; color: #0F172A;
    margin-bottom: 4px; font-variant-numeric: tabular-nums;
  }
  .tl-bar-wrap {
    width: 80%; flex: 1; display: flex; align-items: flex-end;
    background: #F8FAFC; border-radius: 6px 6px 0 0; padding-top: 4px;
  }
  .tl-bar {
    width: 100%; border-radius: 6px 6px 0 0;
    transition: height 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: inset 0 -2px 0 rgba(0,0,0,0.08);
  }
  .tl-bar-wrap:hover .tl-bar {filter: brightness(1.08);}
  .tl-expired-badge {
    margin-top: 4px;
    background: #FEE2E2; color: #B91C1C;
    font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;
  }
  .tl-month {
    color: #64748B; font-size: 0.74rem; font-weight: 600;
    margin-top: 8px; letter-spacing: 0.02em;
  }

  /* Compliance hero (Dashboard) */
  .compliance-hero {
    display: grid; grid-template-columns: minmax(180px, 240px) 1fr;
    gap: 28px; align-items: center;
    background: white; border: 1px solid var(--bd); border-radius: 18px;
    padding: 28px 32px; margin-bottom: 22px;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03);
    position: relative; overflow: hidden;
  }
  .compliance-hero::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #F4845F 0%, #FFB74D 50%, #F4845F 100%);
  }
  .compliance-hero .ch-left {
    border-right: 1px solid var(--bd); padding-right: 28px;
  }
  .compliance-hero .ch-score {
    font-size: 4.5rem; font-weight: 800; line-height: 1;
    letter-spacing: -0.04em; font-variant-numeric: tabular-nums;
  }
  .compliance-hero .ch-score span {font-size: 2rem; font-weight: 700; margin-left: 2px; opacity: 0.8;}
  .compliance-hero .ch-label {
    color: #64748B; font-size: 0.78rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase; margin-top: 4px;
  }
  .compliance-hero .ch-status {
    font-size: 1.15rem; font-weight: 700; margin-bottom: 4px;
    letter-spacing: -0.01em;
  }
  .compliance-hero .ch-msg {color: #475569; font-size: 0.92rem; margin-bottom: 18px;}
  .compliance-hero .ch-bar {
    display: flex; height: 12px; border-radius: 6px;
    overflow: hidden; background: #F1F5F9; margin-bottom: 10px;
  }
  .compliance-hero .ch-bar > div {transition: width 0.4s ease;}
  .compliance-hero .ch-bar-key {
    display: flex; flex-wrap: wrap; gap: 18px;
    font-size: 0.82rem; color: #64748B; font-weight: 500;
    font-variant-numeric: tabular-nums;
  }
  .compliance-hero .ch-bar-key b {margin-right: 4px; font-size: 0.7rem;}

  @media (max-width: 700px) {
    .compliance-hero {grid-template-columns: 1fr; gap: 18px; padding: 22px;}
    .compliance-hero .ch-left {border-right: none; border-bottom: 1px solid var(--bd); padding-right: 0; padding-bottom: 18px;}
    .compliance-hero .ch-score {font-size: 3.5rem;}
  }

  /* Colour legend bar (Matrix page) */
  .legend-bar {
    display: flex; flex-wrap: wrap; align-items: center; gap: 14px;
    padding: 10px 16px; margin-bottom: 18px;
    background: white; border: 1px solid var(--bd); border-radius: 12px;
    font-size: 0.82rem; color: #475569;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03);
  }
  .legend-key {
    font-weight: 700; color: #94A3B8; letter-spacing: 0.08em;
    text-transform: uppercase; font-size: 0.7rem; margin-right: 4px;
  }
  .legend-chip {display: inline-flex; align-items: center; gap: 6px;}
  .legend-swatch {width: 12px; height: 12px; border-radius: 3px; display: inline-block;}

  /* Help box — page-level guidance */
  .help-box {
    background: linear-gradient(180deg, #FFFAF3 0%, #FFF1DF 100%);
    border: 1px solid #FFD9B8;
    border-left: 3px solid #F4845F;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 22px;
  }
  .help-box .help-title {font-weight: 600; color: #0F172A; margin-bottom: 4px; font-size: 0.95rem;}
  .help-box .help-body {color: #64748B; font-size: 0.88rem; line-height: 1.6;}

  /* Tutorial steps — big, friendly, numbered. Written for non-technical users. */
  .tut-step {
    display: flex; gap: 18px; align-items: flex-start;
    background: white; border: 1px solid var(--bd); border-radius: 14px;
    padding: 20px 22px; margin-bottom: 14px;
  }
  .tut-step .tut-num {
    flex: 0 0 44px; width: 44px; height: 44px; border-radius: 50%;
    background: var(--olt); color: var(--or2);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.25rem; font-weight: 800;
  }
  .tut-step .tut-title {font-size: 1.05rem; font-weight: 700; color: var(--t0); margin-bottom: 4px;}
  .tut-step .tut-body {font-size: 0.97rem; color: var(--t2); line-height: 1.7;}
  .tut-step .tut-body b {color: var(--t0);}
  .tut-step .tut-where {
    display: inline-block; margin-top: 8px; padding: 3px 10px; border-radius: 999px;
    background: #EFF6FF; color: #1D4ED8; font-size: 0.8rem; font-weight: 600;
  }
  .tut-section {
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--or); margin: 26px 0 12px 0;
  }

  /* Step cards (welcome page how-to) */
  .step-card {
    background: white; border: 1px solid var(--bd); border-radius: 14px;
    padding: 22px 22px 20px 22px; height: 100%;
    transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03);
  }
  .step-card:hover {transform: translateY(-2px); box-shadow: 0 10px 24px -10px rgba(15,23,42,0.12);}
  .step-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border-radius: 10px;
    background: linear-gradient(135deg, #FFE2C6 0%, #FFCFA1 100%);
    color: #B54A1F; font-weight: 700; font-size: 0.95rem;
    margin-bottom: 14px;
  }
  .step-title {font-weight: 600; color: #0F172A; margin-bottom: 6px; font-size: 1rem;}
  .step-body {color: #64748B; font-size: 0.9rem; line-height: 1.6;}

  /* Hero info card on welcome page */
  .hero-card {
    background: white; border: 1px solid var(--bd); border-radius: 16px;
    padding: 24px 28px; margin-bottom: 22px;
    box-shadow: 0 1px 2px rgba(15,23,42,0.03);
    position: relative; overflow: hidden;
  }
  .hero-card::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #F4845F 0%, #FFB74D 50%, #F4845F 100%);
  }
  .hero-card .hero-title {font-size: 1.05rem; font-weight: 600; color: #0F172A; margin-bottom: 6px;}
  .hero-card .hero-body {color: #475569; line-height: 1.65; font-size: 0.94rem;}

  /* ===== 13. Expanders ===== */
  [data-testid="stExpander"] {
    border: 1px solid var(--bd) !important; border-radius: 12px !important;
    background: var(--sf) !important; box-shadow: 0 1px 2px rgba(15,23,42,0.03) !important;
    margin-bottom: 10px !important; overflow: hidden !important;
  }
  [data-testid="stExpander"] summary {
    padding: 13px 18px !important; font-weight: 600 !important;
    font-size: 0.9rem !important; color: var(--t0) !important;
  }
  [data-testid="stExpander"] summary:hover {background: #F8FAFC !important;}

  /* ===== Responsive: tablet ===== */
  @media (max-width: 900px) {
    .block-container {padding-left: 0.75rem; padding-right: 0.75rem;}
    .brand-header {padding: 14px 18px; border-radius: 0 0 14px 14px;}
    .brand-header h1 {font-size: 1.25rem;}
    .brand-header .tagline {font-size: 0.82rem;}
    .kpi-grid {grid-template-columns: repeat(2, 1fr); gap: 10px;}
    .kpi-tile {padding: 14px 16px;}
    .kpi-tile .value {font-size: 1.85rem;}
    .login-shell {padding: 32px 24px 28px 24px;}
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
    .login-shell {padding: 28px 20px 24px 20px; border-radius: 16px;}
    .login-logo-pill img {height: 38px;}
    .login-shell h1 {font-size: 1.25rem;}
    .login-shell .login-tag {font-size: 0.85rem; margin-bottom: 20px;}
    /* Make dataframes scroll horizontally on mobile rather than squashing */
    [data-testid="stDataFrame"] > div {overflow-x: auto;}
  }

  /* Make the Matrix/dataframe area horizontally scrollable on small viewports */
  [data-testid="stDataFrame"] {max-width: 100%;}

  /* ===== Matrix HTML table ===== */
  .matrix-wrap {overflow-x: auto; margin-bottom: 14px; border-radius: 14px; background: white; border: 1px solid var(--bd); box-shadow: 0 1px 2px rgba(15,23,42,0.03);}
  .matrix-table {width: 100%; border-collapse: collapse; font-size: 0.82rem;}
  .mat-th {background: #F8FAFC; color: #64748B; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; padding: 10px 14px; text-align: left; border-bottom: 2px solid var(--bd); white-space: nowrap;}
  .mat-th-person {min-width: 150px; position: sticky; left: 0; z-index: 2; background: #F8FAFC; border-right: 1px solid var(--bd);}
  .matrix-table tbody tr:hover {background: rgba(248,250,252,0.6);}
  .mat-td {padding: 8px 14px; border-bottom: 1px solid #F1F5F9; white-space: nowrap; font-size: 0.82rem; font-weight: 500; color: #0F172A;}
  .mat-td-person {font-weight: 600; min-width: 150px; position: sticky; left: 0; background: white; border-right: 1px solid var(--bd); z-index: 1;}
  .matrix-table tbody tr:hover .mat-td-person {background: #F8FAFC;}
  .mat-missing {color: #CBD5E1 !important; font-size: 0.8rem !important; font-weight: 400 !important;}
  .mat-lifetime {color: #64748B !important; background: #F8FAFC !important; font-style: italic;}
  /* Matrix stats strip */
  .matrix-stats {display: flex; flex-wrap: wrap; align-items: stretch; margin-bottom: 14px; background: white; border: 1px solid var(--bd); border-radius: 12px; overflow: hidden; box-shadow: 0 1px 2px rgba(15,23,42,0.03);}
  .mstat {display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 12px 22px; border-right: 1px solid var(--bd); flex: 1; min-width: 80px;}
  .mstat:last-child {border-right: none;}
  .mstat-label {font-size: 0.66rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #94A3B8; margin-bottom: 3px;}
  .mstat b {font-size: 1.35rem; font-weight: 700; line-height: 1; font-variant-numeric: tabular-nums; color: #0F172A;}
  @media (max-width: 700px) {.mstat {padding: 10px 12px;} .mstat b {font-size: 1.1rem;} .mstat-label {font-size: 0.6rem;} .matrix-stats {gap: 0;}}
  @media (max-width: 480px) {.mstat {flex: 0 0 50%; border-bottom: 1px solid var(--bd);}}
  /* Required-missing cell */
  .mat-required {background: #FEE2E2 !important; color: #991B1B !important; font-weight: 700 !important; font-size: 0.72rem !important; letter-spacing: 0.04em; text-transform: uppercase;}
  /* Category group header row */
  .mat-cat-header {background: #1E293B !important; color: #94A3B8 !important; font-size: 0.64rem !important; letter-spacing: 0.1em; text-transform: uppercase; text-align: center; padding: 6px 8px !important; border-bottom: 2px solid #0F172A !important;}

  /* ===== People page person-row label ===== */
  .person-expander-label {display: flex; align-items: center; gap: 10px;}
  .compliance-badge {display: inline-flex; align-items: center; gap: 5px; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; white-space: nowrap;}
  .compliance-badge.green {background: #DCFCE7; color: #15803D;}
  .compliance-badge.amber {background: #FEF3C7; color: #B45309;}
  .compliance-badge.red {background: #FEE2E2; color: #B91C1C;}
  .compliance-badge.grey {background: #F1F5F9; color: #64748B;}
</style>
"""


def inject_css() -> None:
    # Must run on every page render — multipage Streamlit does not persist
    # st.markdown output across page navigations, so the CSS must be
    # re-injected each time the page script runs.
    st.markdown(BRAND_CSS, unsafe_allow_html=True)


def loading_overlay() -> None:
    """Full-screen pulsing-logo splash that auto-fades out on first render."""
    if not LOGO_PATH.exists():
        return
    import base64

    b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    st.markdown(
        f"""
        <style>
          @keyframes beacon-fade-out {{
            0%, 70% {{opacity: 1; visibility: visible;}}
            100% {{opacity: 0; visibility: hidden;}}
          }}
          @keyframes beacon-pulse {{
            0%, 100% {{
              transform: scale(1);
              box-shadow: 0 0 0 0 rgba(244,132,95,0.55), 0 0 60px 20px rgba(244,132,95,0.25);
            }}
            50% {{
              transform: scale(1.05);
              box-shadow: 0 0 0 30px rgba(244,132,95,0), 0 0 80px 30px rgba(244,132,95,0.45);
            }}
          }}
          @keyframes beacon-shimmer {{
            0% {{background-position: -200% 0;}}
            100% {{background-position: 200% 0;}}
          }}
          .beacon-splash {{
            position: fixed; inset: 0; z-index: 999999;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            background:
              radial-gradient(800px 500px at 80% 10%, rgba(244,132,95,0.22), transparent 60%),
              radial-gradient(700px 500px at 10% 90%, rgba(14,95,255,0.10), transparent 60%),
              linear-gradient(180deg, #FFFBF6 0%, #F7F4EF 100%);
            animation: beacon-fade-out 1.6s ease-in-out forwards;
            pointer-events: none;
          }}
          .beacon-splash .ring {{
            display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, #FFF8F0 0%, #FFE2C6 100%);
            border: 1px solid #FFD3AC;
            border-radius: 999px;
            padding: 26px 52px;
            animation: beacon-pulse 1.4s ease-in-out infinite;
          }}
          .beacon-splash .ring img {{height: 72px; width: auto; display: block;}}
          .beacon-splash .label {{
            margin-top: 28px;
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.24em;
            text-transform: uppercase;
            color: transparent;
            background: linear-gradient(90deg, #8C7B66 0%, #F4845F 50%, #8C7B66 100%);
            background-size: 200% 100%;
            -webkit-background-clip: text;
            background-clip: text;
            animation: beacon-shimmer 1.8s linear infinite;
          }}
        </style>
        <div class="beacon-splash">
          <div class="ring"><img src="data:image/png;base64,{b64}" alt="Beacon Risk"/></div>
          <div class="label">Loading your dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, tagline: str = "", eyebrow: str = "Beacon Risk") -> None:
    eyebrow_html = f'<div class="eyebrow">{eyebrow}</div>' if eyebrow else ""
    tagline_html = f'<div class="tagline">{tagline}</div>' if tagline else ""
    st.markdown(
        f'<div class="brand-header">{eyebrow_html}<h1>{title}</h1>{tagline_html}</div>',
        unsafe_allow_html=True,
    )


def help_box(title: str, body: str) -> None:
    """Soft info card explaining what a page does. Single-line HTML for parser safety."""
    st.markdown(
        '<div class="help-box">'
        f'<div class="help-title">{title}</div>'
        f'<div class="help-body">{body}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


_TIPS_COOKIE = "beacon_tips_seen"


def page_tour(page_key: str, intro: str, steps: list[tuple[str, str]]) -> None:
    """First-visit pop-up walkthrough for a page, plus a replay button.

    Pops up automatically the first time this browser visits the page
    (remembered via cookie), and can be reopened any time with the
    '💡 How does this page work?' button. Written for non-technical users.
    """

    @st.dialog("💡 How this page works")
    def _tour() -> None:
        st.markdown(f"**{intro}**")
        for i, (title, body) in enumerate(steps, 1):
            st.markdown(
                f'<div class="tut-step" style="margin-bottom:10px;padding:14px 16px;">'
                f'<div class="tut-num" style="flex:0 0 34px;width:34px;height:34px;font-size:1rem;">{i}</div>'
                f'<div><div class="tut-title" style="font-size:0.95rem;">{title}</div>'
                f'<div class="tut-body" style="font-size:0.9rem;">{body}</div></div></div>',
                unsafe_allow_html=True,
            )
        if st.button(
            "Got it — let me try!",
            type="primary",
            use_container_width=True,
            key=f"_tour_ok_{page_key}",
        ):
            st.rerun()

    # Replay button — always available so users can re-read the guide.
    if st.button("💡 How does this page work?", key=f"_tour_btn_{page_key}"):
        _tour()
        return

    # Auto-open once per browser per page.
    state_key = f"_tour_seen_{page_key}"
    if st.session_state.get(state_key):
        return
    st.session_state[state_key] = True
    try:
        from app.auth import _cookies  # lazy import — auth imports branding

        cookies = _cookies()
        raw = cookies.get(_TIPS_COOKIE) or ""
        seen = set(raw.split(",")) if raw else set()
        if page_key in seen:
            return
        seen.add(page_key)
        cookies.set(_TIPS_COOKIE, ",".join(sorted(seen)), max_age=365 * 24 * 3600)
    except Exception:
        return  # cookies unavailable — never risk nagging on every visit
    _tour()


def tut_step(num: int, title: str, body: str, where: str = "") -> None:
    """One big friendly numbered tutorial step. Plain-English help for the Help page."""
    where_html = f'<span class="tut-where">📍 {where}</span>' if where else ""
    st.markdown(
        '<div class="tut-step">'
        f'<div class="tut-num">{num}</div>'
        '<div>'
        f'<div class="tut-title">{title}</div>'
        f'<div class="tut-body">{body}{where_html}</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def tut_section(label: str) -> None:
    """Small orange section label used between tutorial groups."""
    st.markdown(f'<div class="tut-section">{label}</div>', unsafe_allow_html=True)


def colour_legend() -> None:
    """Inline legend explaining the matrix traffic-light colours."""
    items = [
        ("#e57373", "Expired / ≤7 days"),
        ("#ffb74d", "≤30 days"),
        ("#fff176", "≤90 days"),
        ("#a5d6a7", "In date (&gt;90 days)"),
        ("#cfd8dc", "Lifetime (no expiry)"),
    ]
    chips = "".join(
        f'<span class="legend-chip"><span class="legend-swatch" style="background:{c};"></span>{label}</span>'
        for c, label in items
    )
    st.markdown(
        '<div class="legend-bar"><span class="legend-key">KEY</span>' + chips + '</div>',
        unsafe_allow_html=True,
    )


def kpi_row(items: list[dict]) -> None:
    """items: [{label, value, sub, tone}] — tone in (expired|week|month|quarter).
    Single-line HTML to avoid Streamlit's markdown parser closing the block early."""
    tiles_html = "".join(
        f'<div class="kpi-tile {it.get("tone", "")}">'
        f'<div class="kpi-meta"><span class="label">{it["label"]}</span>'
        f'<span class="dot-{it.get("tone", "")}"></span></div>'
        f'<div class="value">{it["value"]}</div>'
        f'<div class="sub">{it.get("sub", "")}</div>'
        f'</div>'
        for it in items
    )
    st.markdown(f'<div class="kpi-grid">{tiles_html}</div>', unsafe_allow_html=True)
