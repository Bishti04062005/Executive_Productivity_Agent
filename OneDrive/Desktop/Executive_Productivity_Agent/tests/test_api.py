
import os
import requests
import pytest

from dotenv import load_dotenv

load_dotenv()


def test_openrouter_api():
    """Test OpenRouter only when explicitly requested."""

    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        pytest.skip(
            "Live API test disabled. "
            "Set RUN_LIVE_API_TESTS=1 to enable."
        )

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        pytest.skip("OPENROUTER_API_KEY is missing.")

    model = os.getenv(
        "OPENROUTER_MODEL",
        "nvidia/nemotron-3-super-120b-a12b:free"
    )

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Reply with the word OK."
                }
            ],
            "temperature": 0,
            "max_tokens": 10
        },
        timeout=30
    )

    assert response.status_code == 200, response.text