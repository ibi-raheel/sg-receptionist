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
