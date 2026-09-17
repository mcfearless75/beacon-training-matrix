import base64
import os

import streamlit as st
import streamlit.components.v1 as components
from streamlit_cookies_controller import CookieController

from app.branding import APP_NAME, BRAND_NAME, BRAND_TAGLINE, LOGO_PATH, SHOW_LOGO, inject_css
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


def _friendly_password_error(e: Exception) -> str:
    msg = str(e).lower()
    if "invalid login" in msg or "invalid" in msg:
        return "Email or password is incorrect."
    if "email not confirmed" in msg:
        return "This email has not been confirmed yet. Use the email-code option once, then you can use a password."
    if "rate limit" in msg:
        return "Too many sign-in attempts. Please wait a few minutes and try again."
    return f"Sign-in failed: {e}"


def _finish_login(session) -> None:
    st.session_state["sb_session"] = session
    st.session_state.pop("otp_stage", None)
    st.session_state.pop("otp_email", None)
    _save_rt_cookie(session)
    st.rerun()


def login_screen():
    load_config()  # validates env at startup; no callback redirect needed for OTP flow
    inject_css()
    # Hide sidebar and collapse button on the login screen — nav must not show before auth
    st.markdown(
        "<style>"
        "[data-testid='stSidebar']{display:none !important;}"
        "[data-testid='collapsedControl']{display:none !important;}"
        "</style>",
        unsafe_allow_html=True,
    )

    # Centre the login using columns — no JS body-class injection needed
    _, col, _ = st.columns([1, 2, 1])

    with col:
        logo_uri = _logo_data_uri() if SHOW_LOGO else None
        logo_html = (
            f'<div class="login-logo-pill"><img src="{logo_uri}" alt="{BRAND_NAME}"/></div>'
            if logo_uri else ""
        )
        st.markdown(
            f"""
            <div class="login-shell">
              {logo_html}
              <div class="login-eyebrow">{BRAND_NAME}</div>
              <h1>Training Matrix</h1>
              <div class="login-tag">Workforce compliance, simplified.<br>
              Sign in with your work email.</div>
              <div class="login-divider"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        method = st.radio(
            "Sign-in method",
            ["Password", "Email code"],
            horizontal=True,
            label_visibility="collapsed",
            key="login_method",
        )

        if method == "Password":
            email = st.text_input(
                "Work email",
                placeholder="you@yourcompany.co.uk",
                label_visibility="collapsed",
                key="pw_email_input",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Password",
                label_visibility="collapsed",
                key="pw_password_input",
            )
            if st.button("Sign in", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Enter your email and password.")
                else:
                    sb = anon_client()
                    try:
                        response = sb.auth.sign_in_with_password(
                            {"email": email.strip(), "password": password}
                        )
                        session = getattr(response, "session", response)
                        if not session:
                            st.error("Sign-in failed. Check the email and password.")
                        else:
                            _finish_login(session)
                    except Exception as e:
                        st.error(_friendly_password_error(e))

        else:
            stage = st.session_state.get("otp_stage", "request_email")

            if stage == "request_email":
                email = st.text_input(
                    "Work email",
                    placeholder="you@yourcompany.co.uk",
                    label_visibility="collapsed",
                    key="otp_email_input",
                )
                if st.button("Send sign-in code", use_container_width=True, type="primary") and email:
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
                    placeholder="Enter your 8-digit code",
                    max_chars=8,
                    label_visibility="collapsed",
                    key="otp_code_input",
                )
                verify_clicked = st.button("Verify and sign in", use_container_width=True, type="primary")
                if st.button("← Use a different email", use_container_width=True):
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
                        _finish_login(session)
                    except Exception as e:
                        st.error(_friendly_otp_error(e))

        st.markdown(
            '<div class="login-footer">'
            f'{BRAND_NAME} <span class="dot">·</span> {BRAND_TAGLINE}'
            ' <span class="dot">·</span> Secure sign-in'
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


_TOUR_COOKIE = "beacon_tour_done"


@st.dialog("👋 Welcome!")
def _welcome_dialog():
    """First-visit welcome pop-up, written in plain English for new users."""
    st.markdown(
        "This app keeps track of **your training and certificates** — "
        "like a logbook that never gets lost.\n\n"
        "Three things worth knowing:\n\n"
        "1. **My Profile** (in the left menu) shows *your* courses and when they run out.\n"
        "2. **Colours are traffic lights** — green is fine, red needs sorting.\n"
        "3. **You can't break anything** by clicking around, so have a look!\n"
    )
    if st.button("Show me how it all works", type="primary", use_container_width=True):
        st.session_state["_welcome_cookie_pending"] = True
        st.switch_page("pages/11_Help.py")
    if st.button("No thanks, let me in", use_container_width=True):
        st.session_state["_welcome_cookie_pending"] = True
        st.rerun()


def _maybe_show_welcome() -> None:
    """Show the welcome pop-up once per browser. Remembered via cookie.

    Mirrors page_tour's timing dance: skip the first script run (the cookie
    component's mount rerun would close the dialog instantly) and defer the
    cookie write until after dismissal for the same reason.
    """
    if st.session_state.pop("_welcome_cookie_pending", False):
        try:
            _cookies().set(_TOUR_COOKIE, "1", max_age=365 * 24 * 3600)
        except Exception:
            pass
    if st.session_state.get("_welcome_done"):
        return
    runs = st.session_state.get("_welcome_runs", 0)
    st.session_state["_welcome_runs"] = runs + 1
    if runs == 0:
        return
    try:
        if _cookies().get(_TOUR_COOKIE):
            st.session_state["_welcome_done"] = True
            return
    except Exception:
        st.session_state["_welcome_done"] = True
        return  # cookies unavailable — don't risk nagging on every visit
    st.session_state["_welcome_done"] = True
    _welcome_dialog()


def _render_sidebar_user():
    """Render signed-in user + Sign out button in the sidebar.
    Guard prevents duplicate widget keys when page scripts also call require_auth."""
    if st.session_state.get("_sidebar_rendered"):
        return
    st.session_state["_sidebar_rendered"] = True
    _maybe_show_welcome()
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
                      "_login_class_cleared"):
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
