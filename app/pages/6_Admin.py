import pandas as pd
import streamlit as st

from app.auth import require_admin
from app.branding import help_box, inject_css, page_header
from beacon.db import service_client
from cron.run_reminders import run as run_cron

require_admin()
inject_css()
page_header("Admin", "User roles, reminder audit log, and manual cron triggers.")
help_box(
    "What's on this page",
    "<b>Users</b> — anyone who's signed into the app. Promote a teammate to <i>admin</i> "
    "to let them edit training types and run reminders. "
    "<b>Reminder log</b> — a record of every reminder email sent, useful for auditing. "
    "<b>Manual run</b> — fire the daily reminder check now instead of waiting for tomorrow's cron.",
)
# Service-role client only instantiated after admin gate passes.
sb = service_client()

st.subheader("Users")
users = sb.table("app_users").select("*").execute().data
st.dataframe(pd.DataFrame(users), use_container_width=True)

with st.expander("Promote / demote a user"):
    user_email = st.text_input("User email (must already exist in auth)")
    new_role = st.selectbox("Role", ["user", "admin"])
    if st.button("Set role"):
        auth_user = sb.table("app_users").select("id").eq("email", user_email).execute().data
        if not auth_user:
            st.error("User has not signed in yet — ask them to log in once, then retry.")
        else:
            sb.table("app_users").update({"role": new_role}).eq("email", user_email).execute()
            st.success("Updated.")
            st.rerun()

st.subheader("Reminder log (last 100)")
log = sb.table("reminder_log").select("*").order("sent_at", desc=True).limit(100).execute().data
st.dataframe(pd.DataFrame(log), use_container_width=True)

st.subheader("Manual run")
if st.button("Run reminder check now"):
    result = run_cron()
    st.json(result)
