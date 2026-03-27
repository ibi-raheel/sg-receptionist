import os
import pytest
from app.config import Settings


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC_test")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "auth_test")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+15551234567")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el_test")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice_test")
    monkeypatch.setenv("APP_BASE_URL", "https://test.up.railway.app")

    settings = Settings()
    assert settings.twilio_account_sid == "AC_test"
    assert settings.anthropic_api_key == "sk-ant-test"
    assert settings.app_base_url == "https://test.up.railway.app"
    assert settings.log_level == "INFO"


def test_settings_loads_business_info():
    settings = Settings.model_construct(
        twilio_account_sid="x", twilio_auth_token="x",
        twilio_phone_number="x", anthropic_api_key="x",
        elevenlabs_api_key="x", elevenlabs_voice_id="x",
        app_base_url="x",
    )
    info = settings.load_business_info()
    assert info["business_name"] == "SG CPA"
    assert "Tax Preparation" in info["services"]


def test_settings_builds_system_prompt():
    settings = Settings.model_construct(
        twilio_account_sid="x", twilio_auth_token="x",
        twilio_phone_number="x", anthropic_api_key="x",
        elevenlabs_api_key="x", elevenlabs_voice_id="x",
        app_base_url="x",
    )
    prompt = settings.build_system_prompt()
    assert "SG CPA" in prompt
    assert "555 Republic Dr" in prompt
    assert "Tax Preparation" in prompt
