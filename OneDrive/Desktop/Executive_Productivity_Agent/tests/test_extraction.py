
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import os
import pytest

from extractor import openrouter_extract


def test_extraction():
    """Test AI extraction only when explicitly requested."""

    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        pytest.skip(
            "Live extraction test disabled. "
            "Set RUN_LIVE_API_TESTS=1 to enable."
        )

    inputs = [
        {
            "type": "email",
            "id": "TEST-001",
            "sender": "Arjun",
            "content": "Send the report tomorrow."
        }
    ]

    result = openrouter_extract(inputs)

    assert result is not None
    assert hasattr(result, "actions")
    assert isinstance(result.actions, list)