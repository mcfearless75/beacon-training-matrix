import base64

import streamlit as st
import streamlit.components.v1 as components

from app.branding import LOGO_PATH, inject_css
from beacon.config import load_config
from beacon.db import anon_client


def get_session():
    return st.session_state.get("sb_session")


def _logo_data_uri() -> str | None:
    if not LOGO_PATH.exists():
        return None
    data = LOGO_PATH.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _fragment_to_query_bridge():
    """Supabase puts magic-link tokens in the URL fragment (#access_token=...).
    Streamlit only reads query params. This JS converts the fragment to a query string
    and reloads, so handle_callback() can read access_token via st.query_params.
    """
    components.html(
        """
        <script>
          (function(){
            const h = window.parent.location.hash;
            if (!h) return;
            if (h.indexOf('access_token=') === -1 && h.indexOf('error=') === -1) return;
            const params = new URLSearchParams(h.substring(1));
            const url = new URL(window.parent.location.href);
            url.hash = '';
            params.forEach((v, k) => url.searchParams.set(k, v));
            window.parent.location.replace(url.toString());
          })();
        </script>
        """,
        height=0,
    )


def login_screen():
    cfg = load_config()
    inject_css()
    _fragment_to_query_bridge()

    logo_uri = _logo_data_uri()
    logo_html = (
        f'<div class="login-logo-pill"><img src="{logo_uri}" alt="Beacon Risk"/></div>'
        if logo_uri else ""
    )
    st.markdown(
        f"""
        <div class="login-shell">
          {logo_html}
          <h1>Beacon Training Matrix</h1>
          <div class="login-tag">Sign in to access your training compliance dashboard.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show any auth error surfaced from the fragment-to-query bridge
    params = st.query_params
    if "error" in params or "error_code" in params:
        st.error(
            "Sign-in link expired or invalid. Please request a new magic link below."
        )
        st.query_params.clear()

    email = st.text_input(
        "Work email", placeholder="you@beaconrisk.co.uk", label_visibility="collapsed"
    )
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
        '</div>',
        unsafe_allow_html=True,
    )


def handle_callback():
    """Read access_token from query params after magic-link redirect.
    Tokens arrive in the URL fragment and are converted to query params by
    `_fragment_to_query_bridge()` (runs on the login screen).
    """
    params = st.query_params
    access_token = params.get("access_token")
    refresh_token = params.get("refresh_token", "")
    if access_token:
        sb = anon_client()
        try:
            response = sb.auth.set_session(access_token, refresh_token)
            # supabase-py 2.x returns an AuthResponse with .session
            session = getattr(response, "session", response)
            st.session_state["sb_session"] = session
        except Exception as e:
            st.error(f"Could not establish session: {e}")
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
