import base64
import os

import streamlit as st
import streamlit.components.v1 as components
from streamlit_cookies_controller import CookieController

from app.branding import LOGO_PATH, inject_css
from beacon.config import load_config
from beacon.db import anon_client

_COOKIE_NAME = "beacon_rt"
_COOKIE_MAX_AGE = 7 * 24 * 3600  # 7 days in seconds


def _auth_enabled() -> bool:
    return os.getenv("AUTH_ENABLED", "false").lower() in ("1", "true", "yes", "on")


def _cookies() -> CookieController:
    """Return a shared CookieController instance (same key = same component slot)."""
    return CookieController(key="_beacon_cc")


def _save_rt_cookie(session) -> None:
    """Persist the refresh token in a browser cookie so sessions survive restarts."""
    rt = getattr(session, "refresh_token", None)
    if rt:
        try:
            _cookies().set(_COOKIE_NAME, rt, max_age=_COOKIE_MAX_AGE)
        except Exception:
            pass


def _clear_rt_cookie() -> None:
    """Remove the persisted refresh token cookie on explicit sign-out."""
    try:
        _cookies().remove(_COOKIE_NAME)
    except Exception:
        pass


def _try_restore_from_cookie() -> bool:
    """On a cold start (session_state empty), attempt to restore the Supabase session
    using the refresh token stored in the browser cookie.
    Returns True if a valid session was restored."""
    try:
        rt = _cookies().get(_COOKIE_NAME)
        if not rt:
            return False
        sb = anon_client()
        result = sb.auth.refresh_session(rt)
        session = getattr(result, "session", None)
        if session:
            st.session_state["sb_session"] = session
            # Update cookie with the new refresh token
            _save_rt_cookie(session)
            return True
    except Exception:
        pass
    return False


def get_session():
    """Return the current session, refreshing the access token if it has expired."""
    session = st.session_state.get("sb_session")
    if session is None:
        return None
    # Attempt a silent token refresh so long-lived sessions don't go stale.
    try:
        sb = anon_client()
        refreshed = sb.auth.set_session(session.access_token, session.refresh_token)
        if refreshed and getattr(refreshed, "session", None):
            st.session_state["sb_session"] = refreshed.session
            return refreshed.session
    except Exception:
        pass  # Token still valid or refresh failed — return existing session
    return session


def _logo_data_uri() -> str | None:
    if not LOGO_PATH.exists():
        return None
    data = LOGO_PATH.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _friendly_otp_error(e: Exception) -> str:
    msg = str(e).lower()
    if "rate limit" in msg:
        return "Too many sign-in attempts. Please wait ~30 minutes and try again."
    if "expired" in msg or "invalid" in msg:
        return "That code is incorrect or has expired. Request a new one."
    return f"Sign-in failed: {e}"


def login_screen():
    load_config()  # validates env at startup; no callback redirect needed for OTP flow
    inject_css()

    # Tag the body so login-only styles activate (atmospheric bg, card layout)
    components.html(
        """
        <script>
          const root = window.parent.document.body;
          if (root && !root.classList.contains('login-active')) {
            root.classList.add('login-active');
          }
        </script>
        """,
        height=0,
    )

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
          <div class="login-tag">Enter your work email — we'll send a sign-in code.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stage = st.session_state.get("otp_stage", "request_email")

    if stage == "request_email":
        email = st.text_input(
            "Work email",
            placeholder="you@beaconrisk.co.uk",
            label_visibility="collapsed",
            key="otp_email_input",
        )
        if st.button("Send sign-in code", use_container_width=True) and email:
            sb = anon_client()
            try:
                sb.auth.sign_in_with_otp({"email": email})
                st.session_state["otp_email"] = email
                st.session_state["otp_stage"] = "verify_code"
                st.rerun()
            except Exception as e:
                st.error(_friendly_otp_error(e))

    elif stage == "verify_code":
        target_email = st.session_state.get("otp_email", "")
        st.info(f"Code sent to **{target_email}**. Check your inbox.")
        code = st.text_input(
            "Sign-in code",
            placeholder="Enter your code",
            max_chars=8,
            label_visibility="collapsed",
            key="otp_code_input",
        )
        verify_clicked = st.button("Verify and sign in", use_container_width=True)
        if st.button("← Use a different email", use_container_width=False):
            st.session_state["otp_stage"] = "request_email"
            st.rerun()
        if verify_clicked and code:
            sb = anon_client()
            try:
                response = sb.auth.verify_otp({
                    "email": target_email,
                    "token": code.strip(),
                    "type": "email",
                })
                session = getattr(response, "session", response)
                st.session_state["sb_session"] = session
                st.session_state.pop("otp_stage", None)
                st.session_state.pop("otp_email", None)
                # Persist refresh token so session survives container restarts
                _save_rt_cookie(session)
                st.rerun()
            except Exception as e:
                st.error(_friendly_otp_error(e))

    st.markdown(
        '<div class="login-footer">'
        'Beacon Risk <span class="dot">•</span> Health & Safety Consultants'
        '</div>',
        unsafe_allow_html=True,
    )


def handle_callback():
    """No-op under OTP flow. Kept for backwards compatibility with require_auth."""
    return


def current_user_role() -> str | None:
    if not _auth_enabled():
        return "admin"  # Demo mode: everyone is admin
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


def current_user_email() -> str | None:
    session = get_session()
    if not session:
        return None
    user = getattr(session, "user", None)
    return getattr(user, "email", None) if user else None


def current_person() -> dict | None:
    """Resolve the signed-in worker to their people row.

    In demo mode (AUTH_ENABLED=false) returns the person stashed in
    ``st.session_state['demo_person']`` if any, otherwise None so the
    worker page can prompt for one.
    """
    if not _auth_enabled():
        return st.session_state.get("demo_person")
    session = get_session()
    if not session:
        return None
    sb = anon_client()
    sb.auth.set_session(session.access_token, session.refresh_token)

    # Primary lookup: by auth_user_id (already linked)
    rows = (
        sb.table("people")
        .select("*")
        .eq("auth_user_id", session.user.id)
        .limit(1)
        .execute()
        .data
        or []
    )
    if rows:
        # Stamp last_login on every session resolution (non-fatal if it fails)
        try:
            from datetime import datetime, timezone
            sb.table("people").update(
                {"last_login": datetime.now(timezone.utc).isoformat()}
            ).eq("id", rows[0]["id"]).execute()
        except Exception:
            pass
        return rows[0]

    # Fallback: match by email and auto-link on first sign-in.
    email = getattr(getattr(session, "user", None), "email", None)
    if not email:
        return None
    email_rows = (
        sb.table("people")
        .select("*")
        .eq("email", email)
        .is_("auth_user_id", "null")
        .limit(1)
        .execute()
        .data
        or []
    )
    if not email_rows:
        return None
    person = email_rows[0]
    try:
        sb.table("people").update({"auth_user_id": session.user.id}).eq("id", person["id"]).execute()
        person["auth_user_id"] = session.user.id
    except Exception:
        pass
    return person


def _render_sidebar_user():
    """Render signed-in user + Sign out button in the sidebar.
    Guard prevents duplicate widget keys when page scripts also call require_auth."""
    if st.session_state.get("_sidebar_rendered"):
        return
    st.session_state["_sidebar_rendered"] = True
    # Remove the login-body class once after login. Guard prevents a new iframe
    # being created on every page navigation, which causes a visible style flicker.
    if not st.session_state.get("_login_class_cleared"):
        st.session_state["_login_class_cleared"] = True
        components.html(
            "<script>window.parent.document.body.classList.remove('login-active');</script>",
            height=0,
        )
    with st.sidebar:
        st.markdown("---")
        if _auth_enabled():
            email = current_user_email() or "Signed in"
            st.markdown(f"**{email}**")
            label = "Sign out"
        else:
            demo_person = st.session_state.get("demo_person")
            name = (demo_person or {}).get("name") if isinstance(demo_person, dict) else None
            st.markdown(f"**{name or 'Demo mode (admin)'}**")
            label = "Reset session" if name else "Clear session"

        if st.button(label, key="_logout_btn", use_container_width=True):
            if _auth_enabled():
                try:
                    sb = anon_client()
                    session = get_session()
                    if session:
                        sb.auth.set_session(session.access_token, session.refresh_token)
                    sb.auth.sign_out()
                except Exception:
                    pass
                _clear_rt_cookie()
            for k in ("sb_session", "otp_stage", "otp_email", "demo_person",
                      "_css_injected", "_login_class_cleared"):
                st.session_state.pop(k, None)
            st.rerun()


def require_worker_or_admin():
    """Gate a page so any signed-in user can access. Used by My Profile."""
    if not _auth_enabled():
        _render_sidebar_user()
        return
    require_auth()


def require_auth():
    if not _auth_enabled():
        _render_sidebar_user()
        return  # Demo mode: no auth gate
    handle_callback()
    if not get_session():
        # Cold start — try to restore from persisted browser cookie before
        # forcing the user through the OTP flow again.
        if _try_restore_from_cookie():
            _render_sidebar_user()
            return
        login_screen()
        st.stop()
    _render_sidebar_user()


def require_admin():
    if not _auth_enabled():
        _render_sidebar_user()
        return  # Demo mode: everyone is admin
    require_auth()
    if current_user_role() != "admin":
        st.error("Admin access required.")
        st.stop()
