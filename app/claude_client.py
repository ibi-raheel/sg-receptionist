import logging
from typing import Optional
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
        conversation_history: Optional[list] = None,
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
