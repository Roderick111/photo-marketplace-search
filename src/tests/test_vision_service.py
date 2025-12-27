"""
Tests for the vision service.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.config import Settings
from src.core.exceptions import VisionAPIError
from src.services.vision_service import (
    _build_system_prompt,
    _extract_json_from_response,
    analyze_image,
    get_media_type,
)


class TestGetMediaType:
    """Tests for media type detection."""

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("test.jpg", "image/jpeg"),
            ("test.jpeg", "image/jpeg"),
            ("test.JPG", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.PNG", "image/png"),
            ("test.webp", "image/webp"),
            ("test.gif", "image/gif"),
        ],
    )
    def test_supported_formats(self, path: str, expected: str) -> None:
        """Should return correct media type for supported formats."""
        assert get_media_type(path) == expected

    def test_unsupported_format_raises(self) -> None:
        """Should raise VisionAPIError for unsupported formats."""
        with pytest.raises(VisionAPIError, match="Unsupported image format"):
            get_media_type("test.bmp")

    def test_no_extension_raises(self) -> None:
        """Should raise VisionAPIError for files without extension."""
        with pytest.raises(VisionAPIError, match="Unsupported image format"):
            get_media_type("testfile")


class TestExtractJsonFromResponse:
    """Tests for JSON extraction from Claude responses."""

    def test_extracts_raw_json(self) -> None:
        """Should extract raw JSON object."""
        text = '{"object_type": "book", "confidence": 0.9}'
        result = _extract_json_from_response(text)
        assert result == '{"object_type": "book", "confidence": 0.9}'

    def test_extracts_from_markdown_code_block(self) -> None:
        """Should extract JSON from markdown code block."""
        text = '```json\n{"object_type": "book"}\n```'
        result = _extract_json_from_response(text)
        assert result == '{"object_type": "book"}'

    def test_extracts_from_plain_code_block(self) -> None:
        """Should extract JSON from plain code block."""
        text = '```\n{"object_type": "book"}\n```'
        result = _extract_json_from_response(text)
        assert result == '{"object_type": "book"}'

    def test_handles_text_before_json(self) -> None:
        """Should extract JSON even with preceding text."""
        text = 'Here is the analysis:\n{"object_type": "book"}'
        result = _extract_json_from_response(text)
        assert result == '{"object_type": "book"}'


class TestBuildSystemPrompt:
    """Tests for system prompt generation."""

    def test_contains_required_elements(self) -> None:
        """System prompt should contain all required elements."""
        prompt = _build_system_prompt()

        assert "book" in prompt
        assert "clothing" in prompt
        assert "electronics" in prompt
        assert "French" in prompt or "FRENCH" in prompt or "français" in prompt.lower()
        assert "JSON" in prompt


class TestAnalyzeImage:
    """Tests for image analysis function."""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Provide mock settings."""
        return Settings(
            anthropic_api_key="test-key",
            claude_model="test-model",
            max_upload_size_mb=10,
            allowed_extensions={".jpg", ".jpeg", ".png", ".webp"},
            upload_dir="uploads",
            vision_api_timeout=30,
            max_concurrent_uploads=10,
        )

    @pytest.mark.asyncio
    async def test_analyze_image_success(
        self,
        tmp_path: Path,
        mock_settings: Settings,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Should successfully analyze image and return result."""
        # Create test image
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(sample_jpeg_bytes)

        # Mock API response
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text='{"object_type": "book", "description": "Roman policier", '
                '"search_queries": [{"query": "livre policier", "confidence": 0.9}], '
                '"confidence": 0.85}'
            )
        ]

        with patch("src.services.vision_service.anthropic.Anthropic") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_response

            result = await analyze_image(str(test_image), mock_settings)

            assert result.object_type == "book"
            assert result.confidence == 0.85
            assert len(result.search_queries) == 1

    @pytest.mark.asyncio
    async def test_analyze_image_file_not_found(
        self,
        mock_settings: Settings,
    ) -> None:
        """Should raise VisionAPIError when file not found."""
        with pytest.raises(VisionAPIError, match="Failed to read image file"):
            await analyze_image("/nonexistent/path.jpg", mock_settings)

    @pytest.mark.asyncio
    async def test_analyze_image_invalid_json_response(
        self,
        tmp_path: Path,
        mock_settings: Settings,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Should raise VisionAPIError for invalid JSON response."""
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(sample_jpeg_bytes)

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is not JSON")]

        with patch("src.services.vision_service.anthropic.Anthropic") as mock_client:
            mock_client.return_value.messages.create.return_value = mock_response

            with pytest.raises(VisionAPIError, match="Failed to analyze image"):
                await analyze_image(str(test_image), mock_settings)

    @pytest.mark.asyncio
    async def test_analyze_image_api_timeout(
        self,
        tmp_path: Path,
        mock_settings: Settings,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Should raise VisionAPIError on API timeout."""
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(sample_jpeg_bytes)

        with patch("src.services.vision_service.anthropic.Anthropic") as mock_client:
            import anthropic

            mock_client.return_value.messages.create.side_effect = anthropic.APITimeoutError(
                request=MagicMock()
            )

            with pytest.raises(VisionAPIError, match="timed out"):
                await analyze_image(str(test_image), mock_settings)
