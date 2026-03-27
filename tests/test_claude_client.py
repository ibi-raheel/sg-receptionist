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
