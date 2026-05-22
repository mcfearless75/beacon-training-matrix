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
        st.image(str(LOGO_PATH), width=160)
    st.markdown("### Beacon Training Matrix")
    role = current_user_role()
    if role:
        st.caption(f"Role: **{role}**")
    st.divider()
    st.markdown(
        """
        **Quick navigation**
        - **Dashboard** — what's expiring
        - **Matrix** — full traffic-light view
        - **People** — workforce records
        - **Training Types** — qualification catalogue
        - **Settings** — import + reminder config
        - **Admin** — audit log + manual reminders
        """
    )

page_header(
    "Welcome to Beacon Training Matrix",
    "Track every employee's training expiry. Get reminders before things lapse. Stay compliant.",
)

# Hero "what does this do" block
st.markdown(
    '<div class="hero-card">'
    '<div class="hero-title">What this app does</div>'
    '<div class="hero-body">'
    'Beacon Training Matrix replaces the spreadsheet you used to track who needs '
    'which training and when it expires. It shows you at a glance what is overdue '
    'and what is coming up, and it emails a daily digest <b>90, 30, and 7 days</b> '
    'before any record expires — and on the day it expires.'
    '</div></div>',
    unsafe_allow_html=True,
)

# Three-step how-to
st.markdown("#### How to use it")
c1, c2, c3 = st.columns(3, gap="medium")

def _step_card(num: str, title: str, body_html: str) -> str:
    return (
        '<div class="step-card">'
        f'<div class="step-num">{num}</div>'
        f'<div class="step-title">{title}</div>'
        f'<div class="step-body">{body_html}</div>'
        '</div>'
    )


with c1:
    st.markdown(
        _step_card(
            "1", "Set up your data",
            "Add your team in <b>People</b>. Add the qualifications you track in <b>Training Types</b>. Or upload your existing spreadsheet in <b>Settings</b>."
        ),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        _step_card(
            "2", "Record completions",
            "On the <b>Matrix</b> page, pick a person and a training type, enter the completion and expiry dates, hit Save. Leave expiry blank for lifetime certificates."
        ),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        _step_card(
            "3", "Stay ahead",
            "Open the <b>Dashboard</b> to see what's expiring. The daily reminder email goes out automatically — configure the recipient in <b>Settings</b>."
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="margin-top: 28px; padding: 14px 18px;
      background: #F4F6FA; border-radius: 10px; color: #5B6B85; font-size: 0.88rem;">
      <b>Tip:</b> Start on the <b>Dashboard</b> to see what needs your attention,
      then move to the <b>Matrix</b> to record updates.
    </div>
    """,
    unsafe_allow_html=True,
)
