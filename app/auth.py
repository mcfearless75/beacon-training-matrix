import streamlit as st

from app.branding import LOGO_PATH, inject_css
from beacon.config import load_config
from beacon.db import anon_client


def get_session():
    return st.session_state.get("sb_session")


def login_screen():
    cfg = load_config()
    inject_css()
    st.markdown('<div class="login-shell">', unsafe_allow_html=True)
    if LOGO_PATH.exists():
        col_logo, _ = st.columns([1, 3])
        with col_logo:
            st.image(str(LOGO_PATH), width=72)
    st.markdown(
        '<h1>Beacon Training Matrix</h1>'
        '<div class="login-tag">Sign in to access your training compliance dashboard.</div>',
        unsafe_allow_html=True,
    )
    email = st.text_input("Work email", placeholder="you@beaconrisk.co.uk", label_visibility="collapsed")
    if st.button("Send magic link", use_container_width=True) and email:
        sb = anon_client()
        sb.auth.sign_in_with_otp({
            "email": email,
            "options": {"email_redirect_to": cfg.app_base_url},
        })
        st.success("Check your inbox — the sign-in link expires in 60 minutes.")
    st.markdown(
        '<div style="margin-top:18px; color:#8896AA; font-size:0.8rem; text-align:center;">'
        'Beacon Risk · Internal training compliance'
        '</div></div>',
        unsafe_allow_html=True,
    )


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
