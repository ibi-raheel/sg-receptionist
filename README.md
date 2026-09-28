<div align="center">

# SG CPA voice receptionist

**A Claude-powered phone receptionist that answers hours, services, and location, and never makes things up.**

<p>
<a href="https://ibiraheel.com/p/sg-receptionist"><img alt="Case study" src="https://img.shields.io/badge/Case%20study-ibiraheel.com-0b0c10?style=for-the-badge&labelColor=c8f560"></a>
</p>

<p>
<img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white">
<img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white">
<img alt="Twilio Voice" src="https://img.shields.io/badge/Twilio%20Voice-F22F46?style=flat-square&logo=twilio&logoColor=white">
<img alt="Anthropic Claude" src="https://img.shields.io/badge/Anthropic%20Claude-191919?style=flat-square&logo=anthropic&logoColor=white">
<img alt="ElevenLabs" src="https://img.shields.io/badge/ElevenLabs-000000?style=flat-square&logo=elevenlabs&logoColor=white">
<img alt="Amazon Polly" src="https://img.shields.io/badge/Amazon%20Polly-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white">
<img alt="pytest" src="https://img.shields.io/badge/pytest-30363D?style=flat-square">
<img alt="Railway" src="https://img.shields.io/badge/Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white">
</p>

</div>

<br>

> **After-hours calls answered, zero hallucinated answers**  
> for SG CPA, a certified public accounting firm in Plano, Texas

## What it did

Twilio hands each utterance to FastAPI, Claude answers from a strict business-facts prompt, ElevenLabs speaks it, and Polly takes over if ElevenLabs fails.

<sub>Outcome: illustrative.</sub>

## How it works

<p align="center"><img src=".github/assets/architecture.svg" alt="Architecture" width="100%"></p>

1. Twilio Gather webhooks instead of media streams: simpler, cheaper, good enough for Q&A calls.
2. System prompt is templated from business_info.json so the same code serves any firm.
3. Claude called with max 256 tokens and temperature 0.3 to keep answers short and literal.
4. ElevenLabs TTS with automatic Polly fallback so a vendor outage never drops a call.
5. Health endpoint and Railway config for one-command deploys.

## Run it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                    # Anthropic, Twilio, ElevenLabs
uvicorn app.main:app --reload --port 8000
```

Point your Twilio number's voice webhook at `POST /voice/incoming`. Deploys as-is to
Railway (`Procfile`, `railway.toml`).

## Repository layout

```
├── app/
│   ├── __init__.py
│   ├── claude_client.py
│   ├── config.py
│   ├── elevenlabs_client.py
│   ├── main.py
│   └── voice_handler.py
├── data/
│   ├── business_info.json
│   └── system_prompt.txt
├── docs/
│   └── superpowers/
├── tests/
│   ├── __init__.py
│   ├── test_claude_client.py
│   ├── test_config.py
│   ├── test_elevenlabs_client.py
│   ├── test_main.py
│   └── test_voice_handler.py
├── Procfile
├── railway.toml
└── requirements.txt
```

---

<div align="center">

<sub>Built by <a href="https://github.com/ibi-raheel">Muhammad Ibrahim Raheel</a> · more work at <a href="https://ibiraheel.com">ibiraheel.com</a></sub>

</div>
