import os
from beacon.config import load_config


def test_load_config_reads_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "srk")
    monkeypatch.setenv("RESEND_API_KEY", "re_x")
    monkeypatch.setenv("APP_BASE_URL", "http://localhost:8501")
    monkeypatch.setenv("SENDER_EMAIL", "noreply@beacon.test")
    monkeypatch.setenv("SENDER_NAME", "Beacon")
    cfg = load_config()
    assert cfg.supabase_url == "https://x.supabase.co"
    assert cfg.resend_api_key == "re_x"


def test_load_config_missing_required_raises(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("APP_BASE_URL", raising=False)
    monkeypatch.delenv("SENDER_EMAIL", raising=False)
    import pytest
    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        load_config()
