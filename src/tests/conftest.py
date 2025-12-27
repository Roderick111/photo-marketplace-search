"""
Pytest configuration and fixtures for Photo to Marketplace Search tests.
"""

import os
from pathlib import Path
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.core.config import Settings
from src.main import app
from src.models.responses import SearchQuery, VisionAnalysisResult


@pytest.fixture
def mock_settings() -> Settings:
    """Provide mock settings for testing."""
    return Settings(
        anthropic_api_key="test-api-key",
        claude_model="claude-sonnet-4-20250514",
        max_upload_size_mb=10,
        allowed_extensions={".jpg", ".jpeg", ".png", ".webp"},
        upload_dir="test_uploads",
        vision_api_timeout=30,
        max_concurrent_uploads=10,
    )


@pytest.fixture
def mock_vision_result() -> VisionAnalysisResult:
    """Provide mock vision analysis result."""
    return VisionAnalysisResult(
        object_type="book",
        description="Roman policier français",
        search_queries=[
            SearchQuery(query="livre policier", confidence=0.9),
            SearchQuery(query="roman thriller", confidence=0.85),
        ],
        confidence=0.92,
    )


@pytest.fixture
def mock_anthropic_client() -> MagicMock:
    """Provide mock Anthropic client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            text='{"object_type": "book", "description": "Roman policier", '
            '"search_queries": [{"query": "livre policier", "confidence": 0.9}], '
            '"confidence": 0.85}'
        )
    ]
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def tmp_upload_dir(tmp_path: Path) -> Path:
    """Provide temporary upload directory."""
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir


@pytest.fixture
def sample_jpeg_bytes() -> bytes:
    """Provide minimal valid JPEG bytes for testing."""
    # Valid JPEG header for testing
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"


@pytest.fixture
def sample_png_bytes() -> bytes:
    """Provide minimal valid PNG bytes for testing."""
    # Minimal 1x1 PNG
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f"
        b"\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """Provide async HTTP client for testing FastAPI endpoints."""
    # Set environment variable for tests
    os.environ["ANTHROPIC_API_KEY"] = "test-api-key"

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_vision_service() -> AsyncMock:
    """Provide mock vision service."""
    mock = AsyncMock()
    mock.analyze_image.return_value = VisionAnalysisResult(
        object_type="book",
        description="Test book",
        search_queries=[SearchQuery(query="test query", confidence=0.9)],
        confidence=0.85,
    )
    return mock


@pytest.fixture(autouse=True)
def set_test_env() -> None:
    """Set test environment variables."""
    os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
