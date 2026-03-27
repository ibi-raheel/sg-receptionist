import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.config import Settings
from app.claude_client import ClaudeClient
from app.elevenlabs_client import ElevenLabsClient
from app.voice_handler import VoiceHandler, AUDIO_DIR

logger = logging.getLogger(__name__)

settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

claude_client = ClaudeClient(
    api_key=settings.anthropic_api_key,
    system_prompt=settings.build_system_prompt(),
)

elevenlabs_client = ElevenLabsClient(
    api_key=settings.elevenlabs_api_key,
    voice_id=settings.elevenlabs_voice_id,
)

voice_handler = VoiceHandler(
    app_base_url=settings.app_base_url,
    claude_client=claude_client,
    elevenlabs_client=elevenlabs_client,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    AUDIO_DIR.mkdir(exist_ok=True)
    logger.info("SG CPA AI Receptionist started")
    yield
    logger.info("SG CPA AI Receptionist shutting down")


app = FastAPI(title="SG CPA AI Receptionist", lifespan=lifespan)
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/voice/incoming")
async def voice_incoming(
    CallSid: str = Form(""),
    From: str = Form(""),
):
    logger.info("Incoming call: sid=%s from=%s", CallSid, From)
    twiml = voice_handler.build_greeting()
    return Response(content=str(twiml), media_type="text/xml")


@app.post("/voice/respond")
async def voice_respond(
    CallSid: str = Form(""),
    SpeechResult: str = Form(""),
):
    logger.info("Speech received: sid=%s text='%s'", CallSid, SpeechResult)

    if not SpeechResult.strip():
        twiml = voice_handler.build_goodbye()
        return Response(content=str(twiml), media_type="text/xml")

    twiml = await voice_handler.handle_speech(SpeechResult, call_sid=CallSid)
    return Response(content=str(twiml), media_type="text/xml")


@app.post("/voice/status")
async def voice_status(
    CallSid: str = Form(""),
    CallStatus: str = Form(""),
    CallDuration: str = Form("0"),
):
    logger.info(
        "Call status: sid=%s status=%s duration=%ss",
        CallSid,
        CallStatus,
        CallDuration,
    )
    voice_handler.cleanup_call(CallSid)
    return {"status": "logged"}
