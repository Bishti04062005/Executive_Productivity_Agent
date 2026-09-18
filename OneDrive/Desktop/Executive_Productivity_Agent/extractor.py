import os
import json
import re
import requests
from pathlib import Path
from dotenv import load_dotenv


# =====================================================
# CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemma-4-26b-a4b-it:free"
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# =====================================================
# PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are an executive productivity assistant.

Your task is to extract actionable commitments from
business communications.

Return ONLY valid JSON.
Do not include Markdown.
Do not include explanations.
Do not include ```json.

Use this exact format:

{
  "actions": [
    {
      "id": "ACTION-001",
      "description": "Short description of the action",
      "owner": "Person responsible or empty string",
      "owner_type": "self, other, or unclear",
      "status": "open, completed, or unclear",
      "due_date": "YYYY-MM-DD or null",
      "waiting_on": [],
      "people": [],
      "source_id": "Source ID",
      "evidence": "Evidence from the communication",
      "uncertainty": "low, medium, or high"
    }
  ]
}

Rules:
1. Extract only meaningful commitments or tasks.
2. Identify the person responsible.
3. Use owner_type 'unclear' when ownership is uncertain.
4. Do not invent deadlines.
5. Use null when a deadline is unavailable.
6. Preserve the source_id.
7. Return valid JSON only.
"""


# =====================================================
# JSON CLEANING
# =====================================================

def extract_json_from_text(text):
    """
    Extract JSON from an AI response.

    Handles:
    - Plain JSON
    - Markdown JSON blocks
    - Additional text around JSON
    """

    if not text or not text.strip():
        raise ValueError(
            "The AI returned an empty response."
        )

    text = text.strip()

    # Remove Markdown code fences
    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*$",
        "",
        text
    )

    text = text.strip()

    # Try parsing the complete response first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "The AI response did not contain valid JSON.\n"
            f"Response received:\n{text[:1000]}"
        )

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as error:
        raise ValueError(
            "The AI response contained invalid JSON.\n"
            f"JSON error: {error}\n"
            f"Response received:\n{text[:1000]}"
        )


# =====================================================
# INPUT PREPARATION
# =====================================================

def prepare_input(input_data):
    """
    Convert input data into readable text for the AI.
    """

    return json.dumps(
        input_data,
        indent=2,
        ensure_ascii=False
    )


# =====================================================
# AI EXTRACTION
# =====================================================

def extract_actions(input_data):
    """
    Send business communications to OpenRouter
    and extract structured actions.
    """

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is missing in .env"
        )

    user_prompt = f"""
Extract all actionable commitments from
the following business communications:

{prepare_input(input_data)}

Return ONLY the required JSON object.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Executive Productivity Agent"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0,
        "max_tokens": 6000
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

    except requests.RequestException as error:
        raise RuntimeError(
            f"Network error while contacting OpenRouter: {error}"
        )

    # Check HTTP status
    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter API error: {response.status_code}\n"
            f"{response.text[:1500]}"
        )

    # Parse API response
    try:
        response_data = response.json()

    except json.JSONDecodeError:
        raise RuntimeError(
            "OpenRouter returned a non-JSON response:\n"
            f"{response.text[:1500]}"
        )

    # Check for API error message
    if "error" in response_data:
        raise RuntimeError(
            f"OpenRouter returned an error:\n"
            f"{response_data['error']}"
        )

    # Extract assistant content
    try:
        choices = response_data.get("choices", [])

        if not choices:
            raise ValueError(
                f"No choices returned by the API:\n"
                f"{response_data}"
            )

        message = choices[0].get("message", {})

        content = message.get("content", "")

    except Exception as error:
        raise RuntimeError(
            f"Could not read AI response: {error}"
        )

    # Some models return content as a list
    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, dict):
                text_parts.append(
                    str(item.get("text", ""))
                )
            else:
                text_parts.append(str(item))

        content = "".join(text_parts)

    # Check empty response
    if not content or not str(content).strip():
        raise RuntimeError(
            "The AI returned an empty content field.\n"
            f"Full API response:\n{response_data}"
        )

    # Convert response to JSON
    extracted_data = extract_json_from_text(
        str(content)
    )

    # Validate expected structure
    if not isinstance(extracted_data, dict):
        raise ValueError(
            "AI response must be a JSON object."
        )

    if "actions" not in extracted_data:
        raise ValueError(
            "AI response does not contain an 'actions' key."
        )

    if not isinstance(extracted_data["actions"], list):
        raise ValueError(
            "The 'actions' value must be a list."
        )

    return extracted_data


# =====================================================
# COMPATIBILITY FUNCTION
# =====================================================

def extract_commitments(input_data):
    """
    Compatibility alias for older app versions.
    """

    return extract_actions(input_data)