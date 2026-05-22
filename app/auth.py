import streamlit as st

from beacon.config import load_config
from beacon.db import anon_client


def get_session():
    return st.session_state.get("sb_session")


def login_screen():
    cfg = load_config()
    st.title("Beacon Training Matrix")
    st.write("Sign in with a magic link.")
    email = st.text_input("Email")
    if st.button("Send magic link") and email:
        sb = anon_client()
        sb.auth.sign_in_with_otp({
            "email": email,
            "options": {"email_redirect_to": cfg.app_base_url},
        })
        st.success("Check your email for the sign-in link.")


def handle_callback():
    """Read access_token from query params after magic-link redirect."""
    params = st.query_params
    if "access_token" in params:
        sb = anon_client()
        session = sb.auth.set_session(
            params["access_token"], params.get("refresh_token", "")
        )
        st.session_state["sb_session"] = session
        st.query_params.clear()
        st.rerun()


def current_user_role() -> str | None:
    session = get_session()
    if not session:
        return None
    sb = anon_client()
    sb.auth.set_session(session.access_token, session.refresh_token)
    row = (
        sb.table("app_users")
        .select("role")
        .eq("id", session.user.id)
        .single()
        .execute()
        .data
    )
    return row["role"] if row else None


def require_auth():
    handle_callback()
    if not get_session():
        login_screen()
        st.stop()


def require_admin():
    require_auth()
    if current_user_role() != "admin":
        st.error("Admin access required.")
        st.stop()
