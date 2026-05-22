"""Supabase client factories.

Two flavours: anon (RLS-enforced) and service-role (bypasses RLS).

When `AUTH_ENABLED=false` (default), `anon_client` returns the service-role
client so the app works without per-user sign-in. Set `AUTH_ENABLED=true` on
Railway to re-enable Supabase magic-link/OTP auth + RLS enforcement.
"""

import os

from supabase import Client, create_client

from beacon.config import load_config


def _auth_enabled() -> bool:
    return os.getenv("AUTH_ENABLED", "false").lower() in ("1", "true", "yes", "on")


def anon_client() -> Client:
    cfg = load_config()
    if not _auth_enabled():
        # Demo / single-tenant mode: use service role so RLS doesn't block reads/writes
        return create_client(cfg.supabase_url, cfg.supabase_service_role_key)
    return create_client(cfg.supabase_url, cfg.supabase_anon_key)


def service_client() -> Client:
    """Service-role client. Bypasses RLS. Used for cron + bulk import."""
    cfg = load_config()
    return create_client(cfg.supabase_url, cfg.supabase_service_role_key)
