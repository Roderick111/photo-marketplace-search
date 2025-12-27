"""
Tests for API routes.
"""

import io
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from src.models.responses import SearchQuery, VisionAnalysisResult


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_healthy(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Health endpoint should return healthy status."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAnalyzeEndpoint:
    """Tests for image analysis endpoint."""

    @pytest.fixture
    def mock_analysis_result(self) -> VisionAnalysisResult:
        """Provide mock analysis result."""
        return VisionAnalysisResult(
            object_type="book",
            description="Roman policier",
            search_queries=[
                SearchQuery(query="livre policier", confidence=0.9),
            ],
            confidence=0.85,
        )

    @pytest.mark.asyncio
    async def test_analyze_valid_image(
        self,
        async_client: AsyncClient,
        mock_analysis_result: VisionAnalysisResult,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Should successfully analyze valid image."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = mock_analysis_result

            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data
            assert "marketplace_links" in data
            assert data["analysis"]["object_type"] == "book"

    @pytest.mark.asyncio
    async def test_analyze_rejects_empty_file(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Should reject empty file with 400."""
        files = {"file": ("test.jpg", io.BytesIO(b""), "image/jpeg")}
        response = await async_client.post("/api/analyze", files=files)

        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_analyze_rejects_invalid_extension(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Should reject file with invalid extension."""
        files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
        response = await async_client.post("/api/analyze", files=files)

        assert response.status_code == 400
        assert "invalid file type" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_analyze_rejects_invalid_magic_numbers(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Should reject file with invalid magic numbers."""
        # File with .jpg extension but not valid JPEG content
        fake_image = b"This is not a real image file"
        files = {"file": ("test.jpg", io.BytesIO(fake_image), "image/jpeg")}
        response = await async_client.post("/api/analyze", files=files)

        assert response.status_code == 400
        assert "magic numbers" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_analyze_handles_api_error(
        self,
        async_client: AsyncClient,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Should return 503 when vision API fails."""
        from src.core.exceptions import VisionAPIError

        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.side_effect = VisionAPIError("API failed")

            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 503
            assert "try again" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_analyze_returns_processing_time(
        self,
        async_client: AsyncClient,
        mock_analysis_result: VisionAnalysisResult,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Should include processing time in response."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = mock_analysis_result

            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()
            assert "processing_time_seconds" in data
            assert isinstance(data["processing_time_seconds"], float)

    @pytest.mark.asyncio
    async def test_analyze_returns_marketplace_links(
        self,
        async_client: AsyncClient,
        mock_analysis_result: VisionAnalysisResult,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Should return marketplace links based on object type."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = mock_analysis_result

            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()
            links = data["marketplace_links"]
            assert len(links) >= 1
            # Book should route to Abebooks
            assert links[0]["marketplace"] == "abebooks"
            assert "abebooks.fr" in links[0]["url"]


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.mark.asyncio
    async def test_root_returns_info(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Root endpoint should return API info."""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
