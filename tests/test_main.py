import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Set env vars BEFORE importing app.main so Settings() picks them up
    import os
    os.environ.update({
        "TWILIO_ACCOUNT_SID": "AC_test",
        "TWILIO_AUTH_TOKEN": "auth_test",
        "TWILIO_PHONE_NUMBER": "+15551234567",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "ELEVENLABS_API_KEY": "el_test",
        "ELEVENLABS_VOICE_ID": "voice_test",
        "APP_BASE_URL": "https://test.up.railway.app",
    })

    import importlib
    import app.main
    importlib.reload(app.main)
    yield TestClient(app.main.app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_voice_incoming_returns_twiml(client):
    response = client.post(
        "/voice/incoming",
        data={"CallSid": "CA123", "From": "+15559876543"},
    )
    assert response.status_code == 200
    assert "text/xml" in response.headers["content-type"]
    assert "<Gather" in response.text
    assert "SG CPA" in response.text


def test_voice_respond_with_empty_speech_returns_goodbye(client):
    response = client.post(
        "/voice/respond",
        data={"CallSid": "CA123", "SpeechResult": ""},
    )
    assert response.status_code == 200
    assert "text/xml" in response.headers["content-type"]
    assert "Goodbye" in response.text or "goodbye" in response.text


def test_voice_status_logs_completion(client):
    response = client.post(
        "/voice/status",
        data={
            "CallSid": "CA123",
            "CallStatus": "completed",
            "CallDuration": "45",
        },
    )
    assert response.status_code == 200
