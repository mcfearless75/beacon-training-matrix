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
    """
    <div style="
      background: white; border: 1px solid #E5E9F2; border-radius: 16px;
      padding: 24px 28px; margin-bottom: 22px;
      box-shadow: 0 4px 14px rgba(13,27,42,0.04);
    ">
      <div style="font-size: 1.1rem; font-weight: 600; color: #0D1B2A; margin-bottom: 8px;">
        What this app does
      </div>
      <div style="color: #5B6B85; line-height: 1.6;">
        Beacon Training Matrix replaces the spreadsheet you used to track who needs
        which training and when it expires. It shows you at a glance what's overdue
        and what's coming up, and it emails a daily digest <b>90, 30, and 7 days</b>
        before any record expires — and on the day it expires.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Three-step how-to
st.markdown("#### How to use it")
c1, c2, c3 = st.columns(3, gap="medium")

step_style = (
    "background: white; border: 1px solid #E5E9F2; border-radius: 14px; "
    "padding: 20px 22px; height: 100%; "
    "box-shadow: 0 2px 8px rgba(13,27,42,0.03);"
)
num_style = (
    "display:inline-block; width:30px; height:30px; line-height:30px; "
    "text-align:center; border-radius:50%; "
    "background:linear-gradient(135deg,#F4845F,#E5663C); color:white; "
    "font-weight:700; font-size:0.9rem; margin-bottom:10px;"
)

with c1:
    st.markdown(
        f"""
        <div style="{step_style}">
          <div style="{num_style}">1</div>
          <div style="font-weight:600; color:#0D1B2A; margin-bottom:6px;">Set up your data</div>
          <div style="color:#5B6B85; font-size:0.9rem; line-height:1.55;">
            Add your team in <b>People</b>. Add the qualifications you track in
            <b>Training Types</b>. Or upload your existing spreadsheet in <b>Settings</b>.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f"""
        <div style="{step_style}">
          <div style="{num_style}">2</div>
          <div style="font-weight:600; color:#0D1B2A; margin-bottom:6px;">Record completions</div>
          <div style="color:#5B6B85; font-size:0.9rem; line-height:1.55;">
            On the <b>Matrix</b> page, click a person + training type and enter the
            completion and expiry dates. Leave expiry blank for lifetime certificates.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f"""
        <div style="{step_style}">
          <div style="{num_style}">3</div>
          <div style="font-weight:600; color:#0D1B2A; margin-bottom:6px;">Stay ahead</div>
          <div style="color:#5B6B85; font-size:0.9rem; line-height:1.55;">
            Open <b>Dashboard</b> to see what's expiring. The daily reminder email goes
            out automatically — configure the recipient in <b>Settings</b>.
          </div>
        </div>
        """,
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
