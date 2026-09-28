# SG CPA AI Phone Receptionist — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a voice-based AI phone receptionist for SG CPA that answers inbound calls via Twilio, understands caller intent via Claude, and responds with natural speech via ElevenLabs.

**Architecture:** FastAPI server receives Twilio webhooks, transcribes caller speech via Twilio's built-in STT, sends text to Claude API for intent detection and response generation, converts response to audio via ElevenLabs TTS, and streams audio back through Twilio. Fallbacks at every layer: Twilio Polly TTS if ElevenLabs fails, pre-recorded message if Claude fails, voicemail if the server is down.

**Tech Stack:** Python 3.12, FastAPI, Twilio Voice SDK (`twilio`), Anthropic Python SDK (`anthropic`), ElevenLabs Python SDK (`elevenlabs`), `httpx` for async HTTP, Railway for deployment.

---

## File Structure

```
sg-cpa-receptionist/
  app/
    __init__.py
    main.py              # FastAPI app, mounts routes
    config.py            # Settings from env vars
    voice_handler.py     # Twilio webhook handlers (TwiML generation)
    claude_client.py     # Claude API wrapper
    elevenlabs_client.py # ElevenLabs TTS wrapper
  data/
    business_info.json   # Business knowledge base
    system_prompt.txt    # Claude system prompt template
  tests/
    __init__.py
    test_config.py
    test_claude_client.py
    test_elevenlabs_client.py
    test_voice_handler.py
    test_main.py
  requirements.txt
  Procfile
  railway.toml
  .env.example
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `Procfile`
- Create: `railway.toml`
- Create: `app/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
twilio==9.3.0
anthropic==0.43.0
elevenlabs==1.15.0
httpx==0.27.0
python-dotenv==1.0.1
pytest==8.3.0
pytest-asyncio==0.24.0
```

- [ ] **Step 2: Create `.env.example`**

```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
ANTHROPIC_API_KEY=your_anthropic_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id
APP_BASE_URL=https://your-app.up.railway.app
LOG_LEVEL=INFO
```

- [ ] **Step 3: Create `Procfile`**

```
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

- [ ] **Step 4: Create `railway.toml`**

```toml
[build]
builder = "nixpacks"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 5
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

- [ ] **Step 5: Create `app/__init__.py` and `tests/__init__.py`**

Both files are empty.

- [ ] **Step 6: Install dependencies and verify**

Run: `cd /Users/ibi/Documents/SG_Receptionist && pip install -r requirements.txt`
Expected: All packages install successfully.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt .env.example Procfile railway.toml app/__init__.py tests/__init__.py
git commit -m "feat: project scaffolding with dependencies and deployment config"
```

---

### Task 2: Configuration Module

**Files:**
- Create: `data/business_info.json`
- Create: `data/system_prompt.txt`
- Test: `tests/test_config.py`
- Create: `app/config.py`

- [ ] **Step 1: Create `data/business_info.json`**

```json
{
  "business_name": "SG CPA",
  "industry": "Certified Public Accounting",
  "hours": {
    "monday": "9:00 AM - 5:00 PM",
    "tuesday": "9:00 AM - 5:00 PM",
    "wednesday": "9:00 AM - 5:00 PM",
    "thursday": "9:00 AM - 5:00 PM",
    "friday": "9:00 AM - 5:00 PM",
    "saturday": "Closed",
    "sunday": "Closed"
  },
  "address": "555 Republic Dr., Plano, TX",
  "phone": "",
  "services": [
    "Accounting",
    "Bookkeeping",
    "Tax Preparation",
    "Payroll Services"
  ],
  "after_hours_message": "Our office is currently closed. Our hours are Monday through Friday, 9 AM to 5 PM. Please call back during business hours."
}
```

- [ ] **Step 2: Create `data/system_prompt.txt`**

```
You are the AI phone receptionist for {business_name}, a {industry} firm.

Your job is to answer inbound phone calls and help callers with basic business information. You must be professional, warm, and concise.

BUSINESS INFORMATION:
- Business Name: {business_name}
- Address: {address}
- Hours of Operation: Monday through Friday, 9:00 AM to 5:00 PM CST. Closed Saturday and Sunday.
- Services: {services}

RESPONSE RULES:
- Keep answers to 1-2 sentences maximum. Callers are listening, not reading.
- Use a professional, friendly tone appropriate for a CPA firm.
- Only provide information listed above. Do not speculate or make up information.
- If asked about pricing, appointments, or specific tax questions, say: "I'd be happy to help with that. Please call us during business hours, Monday through Friday, 9 AM to 5 PM, and one of our team members can assist you."
- If the caller's question is unclear, politely ask them to repeat it.
- Do not discuss topics unrelated to the business.
```

- [ ] **Step 3: Write the failing test for config**

Create `tests/test_config.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it fails**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.config'`

- [ ] **Step 5: Implement `app/config.py`**

```python
import json
from pathlib import Path
from pydantic_settings import BaseSettings


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class Settings(BaseSettings):
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    anthropic_api_key: str
    elevenlabs_api_key: str
    elevenlabs_voice_id: str
    app_base_url: str
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "extra": "ignore"}

    def load_business_info(self) -> dict:
        path = DATA_DIR / "business_info.json"
        with open(path) as f:
            return json.load(f)

    def build_system_prompt(self) -> str:
        info = self.load_business_info()
        template_path = DATA_DIR / "system_prompt.txt"
        template = template_path.read_text()
        return template.format(
            business_name=info["business_name"],
            industry=info["industry"],
            address=info["address"],
            services=", ".join(info["services"]),
        )
```

Note: `pydantic-settings` is a dependency of `pydantic` — add `pydantic-settings==2.5.0` to `requirements.txt` and re-install.

- [ ] **Step 6: Add `pydantic-settings` to requirements and install**

Append `pydantic-settings==2.5.0` to `requirements.txt`.

Run: `pip install pydantic-settings==2.5.0`

- [ ] **Step 7: Run test to verify it passes**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_config.py -v`
Expected: 3 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add app/config.py data/ tests/test_config.py requirements.txt
git commit -m "feat: config module with business info and system prompt builder"
```

---

### Task 3: Claude API Client

**Files:**
- Test: `tests/test_claude_client.py`
- Create: `app/claude_client.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_claude_client.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.claude_client import ClaudeClient


@pytest.fixture
def claude_client():
    return ClaudeClient(
        api_key="sk-ant-test",
        system_prompt="You are a test receptionist for SG CPA.",
    )


@pytest.mark.asyncio
async def test_generate_response_returns_text(claude_client):
    mock_response = MagicMock()
    mock_text_block = MagicMock()
    mock_text_block.type = "text"
    mock_text_block.text = "Our hours are Monday through Friday, 9 AM to 5 PM."
    mock_response.content = [mock_text_block]

    with patch.object(
        claude_client.client.messages, "create", new_callable=AsyncMock, return_value=mock_response
    ):
        result = await claude_client.generate_response("What are your hours?")
        assert result == "Our hours are Monday through Friday, 9 AM to 5 PM."


@pytest.mark.asyncio
async def test_generate_response_handles_api_error(claude_client):
    with patch.object(
        claude_client.client.messages, "create", new_callable=AsyncMock, side_effect=Exception("API timeout")
    ):
        result = await claude_client.generate_response("What are your hours?")
        assert "Monday through Friday" in result  # fallback message


@pytest.mark.asyncio
async def test_generate_response_with_conversation_history(claude_client):
    mock_response = MagicMock()
    mock_text_block = MagicMock()
    mock_text_block.type = "text"
    mock_text_block.text = "Yes, we offer payroll services."
    mock_response.content = [mock_text_block]

    with patch.object(
        claude_client.client.messages, "create", new_callable=AsyncMock, return_value=mock_response
    ) as mock_create:
        history = [
            {"role": "user", "content": "What services do you offer?"},
            {"role": "assistant", "content": "We offer Accounting, Bookkeeping, Tax Preparation, and Payroll Services."},
        ]
        result = await claude_client.generate_response("Do you do payroll?", conversation_history=history)
        assert result == "Yes, we offer payroll services."
        call_args = mock_create.call_args
        assert len(call_args.kwargs["messages"]) == 3  # history + new message
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_claude_client.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.claude_client'`

- [ ] **Step 3: Implement `app/claude_client.py`**

```python
import logging
import anthropic

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I'm sorry, I'm having trouble right now. "
    "Our office hours are Monday through Friday, 9 AM to 5 PM. "
    "Please call back during business hours for assistance."
)


class ClaudeClient:
    def __init__(self, api_key: str, system_prompt: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.system_prompt = system_prompt

    async def generate_response(
        self,
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> str:
        messages = list(conversation_history or [])
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=256,
                temperature=0.3,
                system=self.system_prompt,
                messages=messages,
            )
            for block in response.content:
                if block.type == "text":
                    return block.text
            return FALLBACK_RESPONSE
        except Exception:
            logger.exception("Claude API error")
            return FALLBACK_RESPONSE
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_claude_client.py -v`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/claude_client.py tests/test_claude_client.py
git commit -m "feat: Claude API client with fallback handling"
```

---

### Task 4: ElevenLabs TTS Client

**Files:**
- Test: `tests/test_elevenlabs_client.py`
- Create: `app/elevenlabs_client.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_elevenlabs_client.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_elevenlabs_client.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.elevenlabs_client'`

- [ ] **Step 3: Implement `app/elevenlabs_client.py`**

```python
import logging
import httpx

logger = logging.getLogger(__name__)

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class ElevenLabsClient:
    def __init__(self, api_key: str, voice_id: str):
        self.api_key = api_key
        self.voice_id = voice_id

    async def synthesize(self, text: str) -> bytes | None:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_elevenlabs_client.py -v`
Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/elevenlabs_client.py tests/test_elevenlabs_client.py
git commit -m "feat: ElevenLabs TTS client with error handling"
```

---

### Task 5: Voice Handler (TwiML Generation)

**Files:**
- Test: `tests/test_voice_handler.py`
- Create: `app/voice_handler.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_voice_handler.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_voice_handler.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.voice_handler'`

- [ ] **Step 3: Implement `app/voice_handler.py`**

```python
import logging
import hashlib
import os
from pathlib import Path
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
        self.conversations: dict[str, list[dict]] = {}

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_voice_handler.py -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/voice_handler.py tests/test_voice_handler.py
git commit -m "feat: voice handler with TwiML generation and ElevenLabs/Polly fallback"
```

---

### Task 6: FastAPI Application (Webhook Endpoints)

**Files:**
- Test: `tests/test_main.py`
- Create: `app/main.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_main.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with patch("app.main.Settings") as MockSettings:
        mock_settings = MagicMock()
        mock_settings.twilio_account_sid = "AC_test"
        mock_settings.twilio_auth_token = "auth_test"
        mock_settings.twilio_phone_number = "+15551234567"
        mock_settings.anthropic_api_key = "sk-ant-test"
        mock_settings.elevenlabs_api_key = "el_test"
        mock_settings.elevenlabs_voice_id = "voice_test"
        mock_settings.app_base_url = "https://test.up.railway.app"
        mock_settings.log_level = "INFO"
        mock_settings.build_system_prompt.return_value = "You are a test receptionist."
        MockSettings.return_value = mock_settings

        # Re-import to pick up the mock
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


def test_voice_respond_returns_twiml(client):
    with patch("app.main.voice_handler") as mock_handler:
        mock_response = MagicMock()
        mock_response.__str__ = lambda self: '<?xml version="1.0" ?><Response><Say>Test</Say></Response>'
        mock_handler.handle_speech = AsyncMock(return_value=mock_response)

        response = client.post(
            "/voice/respond",
            data={"CallSid": "CA123", "SpeechResult": "What are your hours?"},
        )
        assert response.status_code == 200


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_main.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.main'`

- [ ] **Step 3: Implement `app/main.py`**

```python
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import Response, JSONResponse
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/test_main.py -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/main.py tests/test_main.py
git commit -m "feat: FastAPI app with Twilio webhook endpoints"
```

---

### Task 7: Run All Tests

**Files:** None (verification only)

- [ ] **Step 1: Run the full test suite**

Run: `cd /Users/ibi/Documents/SG_Receptionist && python -m pytest tests/ -v`
Expected: All 13 tests PASS.

- [ ] **Step 2: Verify the server starts locally**

Run: `cd /Users/ibi/Documents/SG_Receptionist && timeout 5 uvicorn app.main:app --host 0.0.0.0 --port 8000 || true`

This will fail because env vars are missing — that's expected. Verify it fails with a config error, not an import error.

- [ ] **Step 3: Test with env vars set**

Run:
```bash
cd /Users/ibi/Documents/SG_Receptionist && \
TWILIO_ACCOUNT_SID=test TWILIO_AUTH_TOKEN=test TWILIO_PHONE_NUMBER=+1 \
ANTHROPIC_API_KEY=test ELEVENLABS_API_KEY=test ELEVENLABS_VOICE_ID=test \
APP_BASE_URL=http://localhost:8000 \
timeout 3 uvicorn app.main:app --host 0.0.0.0 --port 8000 || true
```

Expected: Server starts, then times out after 3s. Look for "SG CPA AI Receptionist started" in output.

- [ ] **Step 4: Commit (if any fixes were needed)**

```bash
git add -A
git commit -m "fix: any adjustments from integration verification"
```

---

### Task 8: Git Init and Final Commit

**Files:** None

- [ ] **Step 1: Initialize git repo**

```bash
cd /Users/ibi/Documents/SG_Receptionist && git init
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.env
*.egg-info/
dist/
build/
.pytest_cache/
.venv/
```

- [ ] **Step 3: Stage and commit everything**

```bash
git add -A
git commit -m "feat: SG CPA AI Phone Receptionist - initial implementation

Twilio voice webhooks, Claude API for NLU, ElevenLabs TTS with
Twilio Polly fallback. Ready for Railway deployment."
```

---

## Deployment Notes (Post-Implementation)

These are manual steps the business owner performs after the code is built:

1. Create a Railway project and connect the GitHub repo
2. Set all environment variables from `.env.example` in Railway dashboard
3. Purchase a Twilio phone number (972 or 469 area code for Plano, TX)
4. Configure Twilio Voice webhook URL: `https://<railway-app>.up.railway.app/voice/incoming` (POST)
5. Configure Twilio Status callback URL: `https://<railway-app>.up.railway.app/voice/status` (POST)
6. Configure Twilio fallback URL to Twilio voicemail
7. Select and test an ElevenLabs voice (Rachel recommended)
8. Make a test call to verify end-to-end flow
