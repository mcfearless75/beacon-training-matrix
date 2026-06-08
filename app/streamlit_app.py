"""Beacon Training Matrix — main entry point.

Uses st.navigation() so the sidebar adapts to the signed-in user's role:
- Workers (role='user'): only see My Profile.
- Admins (role='admin' or demo mode): see everything.

Page files under app/pages/ are still gated by their own require_auth /
require_admin calls, so direct URL access is also blocked.
"""

import os

import streamlit as st

from app.auth import current_user_role, get_session, require_auth
from app.branding import LOGO_PATH

st.set_page_config(
    page_title="Beacon Training Matrix",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🎓",
    layout="wide",
    initial_sidebar_state="auto",
)

# Reset the sidebar-rendered guard so _render_sidebar_user() only fires once per run.
st.session_state["_sidebar_rendered"] = False

# Check auth state before building nav (read-only — no side effects).
# require_auth() below handles callback processing and the login form.
_auth_on = os.getenv("AUTH_ENABLED", "false").lower() in ("1", "true", "yes", "on")
_authed = not _auth_on or bool(get_session())
_role = (current_user_role() or "user") if _authed else "user"
_is_admin = _role == "admin"

# ---- Page definitions ----
home = st.Page("home.py", title="Home", icon=":material/home:", default=_is_admin)
my_profile = st.Page(
    "pages/0_My_Profile.py",
    title="My Profile",
    icon=":material/person:",
    default=not _is_admin,
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
# st.navigation() is called in every code path so it always suppresses the
# auto-discovered pages/ sidebar. When not authenticated, position="hidden"
# keeps the sidebar blank until after login.
if _authed:
    if _is_admin:
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
else:
    # Not authenticated: suppress auto-discovered sidebar completely.
    # require_auth() below will render the login form and call st.stop().
    pg = st.navigation([my_profile], position="hidden")

# Gate the whole app. In demo mode this is a no-op; in auth mode it shows
# the OTP login screen until a session exists.
require_auth()

pg.run()
