"""
Integration tests for the Photo to Marketplace Search application.

These tests verify the complete flow from image upload to marketplace links.
"""

import io
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from src.models.responses import SearchQuery, VisionAnalysisResult


class TestEndToEndFlow:
    """End-to-end integration tests."""

    @pytest.fixture
    def book_analysis(self) -> VisionAnalysisResult:
        """Book analysis result."""
        return VisionAnalysisResult(
            object_type="book",
            description="Roman policier français",
            search_queries=[
                SearchQuery(query="livre policier", confidence=0.9),
                SearchQuery(query="roman thriller", confidence=0.85),
            ],
            confidence=0.88,
        )

    @pytest.fixture
    def clothing_analysis(self) -> VisionAnalysisResult:
        """Clothing analysis result."""
        return VisionAnalysisResult(
            object_type="clothing",
            description="T-shirt noir homme",
            search_queries=[
                SearchQuery(query="tshirt noir homme", confidence=0.92),
            ],
            confidence=0.9,
        )

    @pytest.fixture
    def electronics_analysis(self) -> VisionAnalysisResult:
        """Electronics analysis result."""
        return VisionAnalysisResult(
            object_type="electronics",
            description="Smartphone Samsung",
            search_queries=[
                SearchQuery(query="telephone samsung", confidence=0.88),
            ],
            confidence=0.85,
        )

    @pytest.mark.asyncio
    async def test_book_routes_to_abebooks(
        self,
        async_client: AsyncClient,
        book_analysis: VisionAnalysisResult,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Book images should generate Abebooks links."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = book_analysis

            files = {"file": ("book.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()

            # Verify analysis
            assert data["analysis"]["object_type"] == "book"

            # Verify marketplace routing
            for link in data["marketplace_links"]:
                assert link["marketplace"] == "abebooks"
                assert "abebooks.fr" in link["url"]

    @pytest.mark.asyncio
    async def test_clothing_routes_to_vinted(
        self,
        async_client: AsyncClient,
        clothing_analysis: VisionAnalysisResult,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Clothing images should generate Vinted links."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = clothing_analysis

            files = {"file": ("shirt.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()

            # Verify analysis
            assert data["analysis"]["object_type"] == "clothing"

            # Verify marketplace routing
            for link in data["marketplace_links"]:
                assert link["marketplace"] == "vinted"
                assert "vinted.fr" in link["url"]

    @pytest.mark.asyncio
    async def test_electronics_routes_to_leboncoin(
        self,
        async_client: AsyncClient,
        electronics_analysis: VisionAnalysisResult,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Electronics images should generate Leboncoin links."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = electronics_analysis

            files = {"file": ("phone.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()

            # Verify analysis
            assert data["analysis"]["object_type"] == "electronics"

            # Verify marketplace routing
            for link in data["marketplace_links"]:
                assert link["marketplace"] == "leboncoin"
                assert "leboncoin.fr" in link["url"]

    @pytest.mark.asyncio
    async def test_png_image_accepted(
        self,
        async_client: AsyncClient,
        book_analysis: VisionAnalysisResult,
        sample_png_bytes: bytes,
    ) -> None:
        """PNG images should be accepted."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = book_analysis

            files = {"file": ("test.png", io.BytesIO(sample_png_bytes), "image/png")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_response_includes_all_required_fields(
        self,
        async_client: AsyncClient,
        book_analysis: VisionAnalysisResult,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Response should include all required fields."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = book_analysis

            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "analysis" in data
            assert "marketplace_links" in data
            assert "processing_time_seconds" in data

            # Verify analysis structure
            analysis = data["analysis"]
            assert "object_type" in analysis
            assert "description" in analysis
            assert "search_queries" in analysis
            assert "confidence" in analysis

            # Verify marketplace link structure
            for link in data["marketplace_links"]:
                assert "marketplace" in link
                assert "query" in link
                assert "url" in link

    @pytest.mark.asyncio
    async def test_processing_time_reasonable(
        self,
        async_client: AsyncClient,
        book_analysis: VisionAnalysisResult,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Processing time should be recorded and reasonable."""
        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.return_value = book_analysis

            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 200
            data = response.json()

            # Processing time should be positive and reasonable
            assert data["processing_time_seconds"] >= 0
            # Mock should be fast, real API would be 2-5 seconds
            assert data["processing_time_seconds"] < 30


class TestErrorHandling:
    """Tests for error scenarios."""

    @pytest.mark.asyncio
    async def test_unsupported_file_type(
        self,
        async_client: AsyncClient,
    ) -> None:
        """Should handle unsupported file types gracefully."""
        files = {"file": ("test.bmp", io.BytesIO(b"fake data"), "image/bmp")}
        response = await async_client.post("/api/analyze", files=files)

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_vision_api_failure(
        self,
        async_client: AsyncClient,
        sample_jpeg_bytes: bytes,
    ) -> None:
        """Should handle Vision API failures gracefully."""
        from src.core.exceptions import VisionAPIError

        with patch("src.api.routes.vision_service.analyze_image") as mock_analyze:
            mock_analyze.side_effect = VisionAPIError("API unavailable")

            files = {"file": ("test.jpg", io.BytesIO(sample_jpeg_bytes), "image/jpeg")}
            response = await async_client.post("/api/analyze", files=files)

            assert response.status_code == 503
            # Should not expose internal error details
            assert "unavailable" not in response.json()["detail"].lower()
            assert "try again" in response.json()["detail"].lower()
