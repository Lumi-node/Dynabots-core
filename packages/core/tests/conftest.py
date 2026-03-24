"""Pytest configuration for dynabots-core tests."""

import sys
from pathlib import Path

# Add the package to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


@pytest.fixture
def sample_metadata():
    """Provide sample metadata for tests."""
    return {
        "user_id": "test_user_123",
        "workflow_id": "wf_456",
        "step": 1,
    }
