import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class ElevenLabsClient:
    def __init__(self, api_key: str, voice_id: str):
        self.api_key = api_key
        self.voice_id = voice_id

    async def synthesize(self, text: str) -> Optional[bytes]:
        url = ELEVENLABS_TTS_URL.format(voice_id=self.voice_id)
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.8,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(
                        "ElevenLabs API error: %s %s", response.status_code, response.text
                    )
                    return None
        except Exception:
            logger.exception("ElevenLabs request failed")
            return None
