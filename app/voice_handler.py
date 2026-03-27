import logging
import hashlib
from pathlib import Path
from typing import Dict, List
from twilio.twiml.voice_response import VoiceResponse, Gather

logger = logging.getLogger(__name__)

AUDIO_DIR = Path("/tmp/sg_cpa_audio")
AUDIO_DIR.mkdir(exist_ok=True)


def save_audio_temp(audio_bytes: bytes, call_sid: str) -> str:
    filename = f"resp_{hashlib.md5(call_sid.encode() + audio_bytes[:16]).hexdigest()[:12]}.mp3"
    path = AUDIO_DIR / filename
    path.write_bytes(audio_bytes)
    return f"/audio/{filename}"


class VoiceHandler:
    def __init__(self, app_base_url: str, claude_client, elevenlabs_client):
        self.app_base_url = app_base_url
        self.claude_client = claude_client
        self.elevenlabs_client = elevenlabs_client
        self.conversations: Dict[str, List[dict]] = {}

    def build_greeting(self) -> VoiceResponse:
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action="/voice/respond",
            method="POST",
            speech_timeout="5",
            language="en-US",
        )
        gather.say(
            "Thank you for calling SG CPA. How can I help you today?",
            voice="Polly.Joanna",
        )
        response.append(gather)
        response.say(
            "I didn't catch that. Thank you for calling SG CPA. Goodbye.",
            voice="Polly.Joanna",
        )
        return response

    async def handle_speech(self, speech_text: str, call_sid: str) -> VoiceResponse:
        history = self.conversations.get(call_sid, [])

        ai_response = await self.claude_client.generate_response(
            speech_text, conversation_history=history
        )

        history.append({"role": "user", "content": speech_text})
        history.append({"role": "assistant", "content": ai_response})
        self.conversations[call_sid] = history

        response = VoiceResponse()

        audio_bytes = await self.elevenlabs_client.synthesize(ai_response)
        if audio_bytes:
            audio_path = save_audio_temp(audio_bytes, call_sid)
            audio_url = f"{self.app_base_url}{audio_path}"
            gather = Gather(
                input="speech",
                action="/voice/respond",
                method="POST",
                speech_timeout="5",
                language="en-US",
            )
            gather.play(audio_url)
            response.append(gather)
        else:
            logger.warning("ElevenLabs failed, falling back to Twilio TTS")
            gather = Gather(
                input="speech",
                action="/voice/respond",
                method="POST",
                speech_timeout="5",
                language="en-US",
            )
            gather.say(ai_response, voice="Polly.Joanna")
            response.append(gather)

        response.say(
            "Thank you for calling SG CPA. Have a great day. Goodbye.",
            voice="Polly.Joanna",
        )
        return response

    def build_goodbye(self) -> VoiceResponse:
        response = VoiceResponse()
        response.say(
            "Thank you for calling SG CPA. Have a great day. Goodbye.",
            voice="Polly.Joanna",
        )
        response.hangup()
        return response

    def cleanup_call(self, call_sid: str) -> None:
        self.conversations.pop(call_sid, None)
