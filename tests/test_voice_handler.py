import pytest
from unittest.mock import AsyncMock, patch
from app.voice_handler import VoiceHandler


@pytest.fixture
def handler():
    return VoiceHandler(
        app_base_url="https://test.up.railway.app",
        claude_client=AsyncMock(),
        elevenlabs_client=AsyncMock(),
    )


def test_build_greeting_twiml(handler):
    twiml = handler.build_greeting()
    xml = str(twiml)
    assert "<Say" in xml or "<Play" in xml
    assert "<Gather" in xml
    assert 'action="/voice/respond"' in xml
    assert 'input="speech"' in xml


@pytest.mark.asyncio
async def test_handle_speech_returns_twiml_with_audio(handler):
    handler.claude_client.generate_response = AsyncMock(
        return_value="Our hours are Monday through Friday, 9 AM to 5 PM."
    )
    handler.elevenlabs_client.synthesize = AsyncMock(return_value=b"fake_audio")

    with patch("app.voice_handler.save_audio_temp", return_value="/audio/resp_123.mp3"):
        twiml = await handler.handle_speech("What are your hours?", call_sid="CA123")
        xml = str(twiml)
        assert "<Play" in xml
        assert "<Gather" in xml  # listens for follow-up


@pytest.mark.asyncio
async def test_handle_speech_falls_back_to_twilio_tts(handler):
    handler.claude_client.generate_response = AsyncMock(
        return_value="Our hours are Monday through Friday, 9 AM to 5 PM."
    )
    handler.elevenlabs_client.synthesize = AsyncMock(return_value=None)  # ElevenLabs failed

    twiml = await handler.handle_speech("What are your hours?", call_sid="CA123")
    xml = str(twiml)
    assert "<Say" in xml
    assert "Monday through Friday" in xml


def test_build_goodbye_twiml(handler):
    twiml = handler.build_goodbye()
    xml = str(twiml)
    assert "<Say" in xml
    assert "goodbye" in xml.lower() or "thank" in xml.lower()
