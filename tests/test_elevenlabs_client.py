import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.elevenlabs_client import ElevenLabsClient


@pytest.fixture
def tts_client():
    return ElevenLabsClient(api_key="el_test", voice_id="voice_test")


@pytest.mark.asyncio
async def test_synthesize_returns_audio_bytes(tts_client):
    fake_audio = b"\xff\xfb\x90\x00" + b"\x00" * 100  # fake MP3 header

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = fake_audio

    with patch("app.elevenlabs_client.httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        audio = await tts_client.synthesize("Hello, thank you for calling SG CPA.")
        assert audio == fake_audio
        assert len(audio) > 0


@pytest.mark.asyncio
async def test_synthesize_returns_none_on_error(tts_client):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("app.elevenlabs_client.httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        audio = await tts_client.synthesize("Hello")
        assert audio is None
