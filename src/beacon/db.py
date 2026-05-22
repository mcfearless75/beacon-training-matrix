"""Supabase client factories.

Two flavours: anon (RLS-enforced, used by the Streamlit app) and service-role
(bypasses RLS, used by the cron reminder job only).
"""

from supabase import create_client, Client

from beacon.config import load_config


def anon_client() -> Client:
    cfg = load_config()
    return create_client(cfg.supabase_url, cfg.supabase_anon_key)


def service_client() -> Client:
    """Service-role client. Bypasses RLS. Only for cron job."""
    cfg = load_config()
    return create_client(cfg.supabase_url, cfg.supabase_service_role_key)
