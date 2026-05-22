import streamlit as st

from app.auth import current_user_role, require_auth
from app.branding import LOGO_PATH, inject_css, loading_overlay, page_header

st.set_page_config(
    page_title="Beacon Training Matrix",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🎓",
    layout="wide",
    initial_sidebar_state="auto",
)
require_auth()
inject_css()
loading_overlay()

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=140)
    st.markdown("### Beacon Training Matrix")
    st.caption(f"Signed in · **{current_user_role() or 'user'}**")
    st.divider()
    st.caption("Use the navigation above to move between sections.")

page_header(
    "Welcome to Beacon Training Matrix",
    "Real-time view of training expiry and compliance across the workforce.",
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### Dashboard")
    st.caption("At-a-glance counts of what's expired and what's expiring soon.")
with c2:
    st.markdown("#### Matrix")
    st.caption("Traffic-light grid of every person against every training type.")
with c3:
    st.markdown("#### Admin")
    st.caption("Manual reminder run, user management, and audit log.")

st.markdown(
    "<div style='margin-top:24px; color:#5B6B85;'>"
    "Tip: open <b>Dashboard</b> to see live counts, or jump straight to <b>Matrix</b> for the full grid."
    "</div>",
    unsafe_allow_html=True,
)
