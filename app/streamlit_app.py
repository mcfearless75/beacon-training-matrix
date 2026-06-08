"""Beacon Training Matrix — main entry point.

Uses st.navigation() so the sidebar adapts to the signed-in user's role:
- Workers (role='user'): only see My Profile.
- Admins (role='admin' or demo mode): see everything.

Page files under app/pages/ are still gated by their own require_auth /
require_admin calls, so direct URL access is also blocked.
"""

import streamlit as st

from app.auth import current_user_role, require_auth
from app.branding import LOGO_PATH

st.set_page_config(
    page_title="Beacon Training Matrix",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🎓",
    layout="wide",
    initial_sidebar_state="auto",
)

# Gate the whole app. In demo mode this is a no-op; in auth mode it shows
# the OTP login screen until a session exists.
require_auth()

role = current_user_role() or "user"
is_admin = role == "admin"


# ---- Page definitions ----
home = st.Page("home.py", title="Home", icon=":material/home:", default=is_admin)
my_profile = st.Page(
    "pages/0_My_Profile.py",
    title="My Profile",
    icon=":material/person:",
    default=not is_admin,
)
dashboard = st.Page("pages/1_Dashboard.py", title="Dashboard", icon=":material/dashboard:")
matrix = st.Page("pages/2_Matrix.py", title="Matrix", icon=":material/grid_view:")
people = st.Page("pages/3_People.py", title="People", icon=":material/group:")
training_types = st.Page(
    "pages/4_Training_Types.py", title="Training Types", icon=":material/school:"
)
approvals = st.Page(
    "pages/5_Approvals.py", title="Approvals", icon=":material/fact_check:"
)
admin_page = st.Page(
    "pages/6_Admin.py", title="Admin", icon=":material/admin_panel_settings:"
)
profile = st.Page("pages/7_Profile.py", title="Profile", icon=":material/badge:")
timeline = st.Page("pages/8_Timeline.py", title="Timeline", icon=":material/calendar_month:")
audit_report = st.Page(
    "pages/9_Audit_Report.py", title="Audit Report", icon=":material/print:"
)
settings = st.Page("pages/10_Settings.py", title="Settings", icon=":material/settings:")


# ---- Role-aware navigation ----
if is_admin:
    nav = {
        "": [home, my_profile],
        "Workforce": [dashboard, matrix, people, training_types],
        "Reviews": [approvals, audit_report],
        "Drill-down": [profile, timeline],
        "Setup": [admin_page, settings],
    }
else:
    # Workers only see their own profile. Direct URL access to other pages
    # is still blocked by require_admin() at the top of each admin page.
    nav = [my_profile]

pg = st.navigation(nav, position="sidebar")
pg.run()
