"""Environment-driven configuration for Beacon Training Matrix.

`load_config` reads required values from `os.environ`. Entry points (Streamlit
app, cron script) are responsible for calling `dotenv.load_dotenv()` once at
startup before invoking `load_config`. Keeping dotenv out of this module keeps
tests deterministic — `monkeypatch.setenv/delenv` is authoritative.
"""

from dataclasses import dataclass
import os

REQUIRED = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
]

# Only needed by the reminder cron / anything that actually sends email.
# Deployments without email (e.g. the prospect sandbox) can omit them.
EMAIL_REQUIRED = [
    "RESEND_API_KEY",
    "APP_BASE_URL",
    "SENDER_EMAIL",
]


@dataclass(frozen=True)
class Config:
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    resend_api_key: str
    app_base_url: str
    sender_email: str
    sender_name: str


def load_config(require_email: bool = False) -> Config:
    required = REQUIRED + (EMAIL_REQUIRED if require_email else [])
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")
    app_base_url = os.getenv("APP_BASE_URL", "")
    if app_base_url and not (
        app_base_url.startswith("https://") or app_base_url.startswith("http://localhost")
    ):
        raise RuntimeError("APP_BASE_URL must be https:// (or http://localhost for dev)")
    return Config(
        supabase_url=os.environ["SUPABASE_URL"],
        supabase_anon_key=os.environ["SUPABASE_ANON_KEY"],
        supabase_service_role_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        resend_api_key=os.getenv("RESEND_API_KEY", ""),
        app_base_url=app_base_url,
        sender_email=os.getenv("SENDER_EMAIL", ""),
        sender_name=os.getenv("SENDER_NAME", os.getenv("APP_NAME", "Beacon Training Matrix")),
    )
