import pandas as pd
import streamlit as st

from app.auth import require_admin
from app.branding import help_box, inject_css, page_header, page_tour
from beacon.db import service_client
from cron.run_reminders import run as run_cron

require_admin()
inject_css()
page_header("Admin", "User management, reminder log, and manual cron triggers.")
page_tour(
    "admin",
    "The keys to the app — who can sign in and what they can see.",
    [
        ("Invite a user",
         "Type their email, pick a role, press send. They get a sign-in link by email — "
         "no password needed."),
        ("What roles mean",
         "<b>Admin</b> sees and manages everything. <b>User</b> only sees their own profile."),
        ("Reminder log",
         "A record of the automatic emails the app has already sent — nothing for you to do."),
    ],
)
help_box(
    "What's on this page",
    "<b>Invite user</b> — create a new login and send them a magic link by email. "
    "<b>Users</b> — everyone who has signed in. Promote a teammate to <i>admin</i> "
    "to let them edit training types and run reminders. "
    "<b>Reminder log</b> — a record of every reminder email sent. "
    "<b>Manual run</b> — fire the daily reminder check now.",
)

sb = service_client()

# ── Invite a new user ─────────────────────────────────────────────────────────
st.subheader("Invite a new user")
st.caption(
    "Creates the account and sends a magic-link sign-in email. "
    "Role is applied immediately — no need to promote afterwards."
)
with st.form("invite_user_form", clear_on_submit=True):
    inv_email = st.text_input("Email address", placeholder="colleague@beaconrisk.co.uk")
    inv_role = st.selectbox("Role", ["user", "admin"])
    invited = st.form_submit_button("Send invite", type="primary", use_container_width=False)

if invited:
    if not inv_email or "@" not in inv_email:
        st.error("Enter a valid email address.")
    else:
        try:
            result = sb.auth.admin.invite_user_by_email(inv_email)
            user_id = result.user.id
            # Pre-provision role in app_users so they land with the right access.
            sb.table("app_users").upsert(
                {"id": user_id, "email": inv_email, "role": inv_role},
                on_conflict="id",
            ).execute()
            st.success(
                f"Magic link sent to **{inv_email}**. "
                f"Role set to **{inv_role}**. "
                "They'll be prompted to sign in on first click."
            )
        except Exception as exc:
            err = str(exc).lower()
            if "already registered" in err or "already been registered" in err:
                st.warning(
                    f"**{inv_email}** already has an account. "
                    "Use 'Promote / demote a user' below to change their role."
                )
            else:
                st.error(f"Invite failed: {exc}")

st.divider()

# ── Existing users ────────────────────────────────────────────────────────────
st.subheader("Users")
users = sb.table("app_users").select("*").order("created_at", desc=True).execute().data
if users:
    st.dataframe(
        pd.DataFrame(users)[["email", "role", "created_at"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No users yet.")

with st.expander("Promote / demote a user"):
    user_email = st.text_input("User email (must already exist in auth)")
    new_role = st.selectbox("Role", ["user", "admin"], key="promote_role")
    if st.button("Set role", type="primary"):
        auth_user = (
            sb.table("app_users").select("id").eq("email", user_email).execute().data
        )
        if not auth_user:
            st.error("User has not signed in yet — ask them to log in once, then retry.")
        else:
            sb.table("app_users").update({"role": new_role}).eq("email", user_email).execute()
            st.success(f"Role updated to **{new_role}**.")
            st.rerun()

st.divider()

# ── Reminder log ──────────────────────────────────────────────────────────────
st.subheader("Reminder log (last 100)")
log = (
    sb.table("reminder_log")
    .select("*")
    .order("sent_at", desc=True)
    .limit(100)
    .execute()
    .data
)
if log:
    st.dataframe(pd.DataFrame(log), use_container_width=True, hide_index=True)
else:
    st.info("No reminder emails logged yet.")

st.divider()

# ── Manual cron trigger ───────────────────────────────────────────────────────
st.subheader("Manual run")
st.caption("Fires the daily reminder check immediately — same logic as the overnight cron.")
if st.button("Run reminder check now"):
    result = run_cron()
    st.json(result)
