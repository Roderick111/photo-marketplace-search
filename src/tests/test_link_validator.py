"""
Tests for link validator service.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.models.responses import MarketplaceLink
from src.services.link_validator import (
    check_for_results,
    validate_marketplace_links,
    validate_single_link,
)


class TestCheckForResults:
    """Tests for HTML result detection."""

    def test_abebooks_with_results(self):
        """Should detect results when product items present."""
        html = """
        <html><body>
            <div class="result-item">Book 1</div>
            <div class="result-item">Book 2</div>
        </body></html>
        """
        assert check_for_results(html, "abebooks") is True

    def test_abebooks_no_results(self):
        """Should detect no results from text indicator."""
        html = """
        <html><body>
            <p>Aucun résultat trouvé pour votre recherche</p>
        </body></html>
        """
        assert check_for_results(html, "abebooks") is False

    def test_abebooks_no_results_english(self):
        """Should detect no results from English text."""
        html = """
        <html><body>
            <p>No results found for your search</p>
        </body></html>
        """
        assert check_for_results(html, "abebooks") is False

    def test_vinted_with_results(self):
        """Should detect Vinted results."""
        html = '<html><body><div class="feed-grid__item">Item</div></body></html>'
        assert check_for_results(html, "vinted") is True

    def test_vinted_no_results(self):
        """Should detect no Vinted results."""
        html = "<html><body><p>Aucun article correspondant</p></body></html>"
        assert check_for_results(html, "vinted") is False

    def test_leboncoin_with_results(self):
        """Should detect Leboncoin results."""
        html = '<html><body><div data-qa-id="aditem_container">Ad</div></body></html>'
        assert check_for_results(html, "leboncoin") is True

    def test_leboncoin_no_results(self):
        """Should detect no Leboncoin results."""
        html = "<html><body><p>Aucune annonce trouvée</p></body></html>"
        assert check_for_results(html, "leboncoin") is False

    def test_unknown_marketplace_defaults_true(self):
        """Unknown marketplace should default to having results."""
        html = "<html><body>Some content</body></html>"
        assert check_for_results(html, "unknown") is True

    def test_empty_html_defaults_true(self):
        """Empty HTML should default to having results (fail open)."""
        html = ""
        assert check_for_results(html, "abebooks") is True


class TestValidateSingleLink:
    """Tests for single link validation."""

    @pytest.fixture
    def sample_link(self) -> MarketplaceLink:
        """Provide sample marketplace link."""
        return MarketplaceLink(
            marketplace="abebooks",
            query="livre test",
            url="https://www.abebooks.fr/servlet/SearchResults?kn=livre%20test",
        )

    @pytest.mark.asyncio
    async def test_validates_link_with_results(self, sample_link: MarketplaceLink):
        """Should return True for link with results."""
        mock_html = '<html><body><div class="result-item">Book</div></body></html>'

        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.raise_for_status = MagicMock()

        with patch("src.services.link_validator.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            link, has_results = await validate_single_link(sample_link)

            assert has_results is True
            assert link == sample_link

    @pytest.mark.asyncio
    async def test_validates_link_no_results(self, sample_link: MarketplaceLink):
        """Should return False for link without results."""
        mock_html = "<html><body><p>Aucun résultat</p></body></html>"

        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.raise_for_status = MagicMock()

        with patch("src.services.link_validator.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            link, has_results = await validate_single_link(sample_link)

            assert has_results is False
            assert link == sample_link

    @pytest.mark.asyncio
    async def test_timeout_returns_true(self, sample_link: MarketplaceLink):
        """Should return True (fail open) on timeout."""
        with patch("src.services.link_validator.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            link, has_results = await validate_single_link(sample_link)

            assert has_results is True  # Fail open

    @pytest.mark.asyncio
    async def test_connection_error_returns_true(self, sample_link: MarketplaceLink):
        """Should return True (fail open) on connection error."""
        with patch("src.services.link_validator.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            link, has_results = await validate_single_link(sample_link)

            assert has_results is True  # Fail open


class TestValidateMarketplaceLinks:
    """Tests for bulk link validation."""

    @pytest.fixture
    def sample_links(self) -> list[MarketplaceLink]:
        """Provide sample marketplace links."""
        return [
            MarketplaceLink(marketplace="abebooks", query="book1", url="https://example.com/1"),
            MarketplaceLink(marketplace="abebooks", query="book2", url="https://example.com/2"),
            MarketplaceLink(marketplace="abebooks", query="book3", url="https://example.com/3"),
        ]

    @pytest.mark.asyncio
    async def test_filters_empty_results(self, sample_links: list[MarketplaceLink]):
        """Should filter out links with no results."""

        async def mock_validate(link: MarketplaceLink, timeout: float):
            # First link has results, others don't
            if "1" in link.url:
                return (link, True)
            return (link, False)

        with patch("src.services.link_validator.validate_single_link", side_effect=mock_validate):
            result = await validate_marketplace_links(sample_links)

            assert len(result) == 1
            assert "1" in result[0].url

    @pytest.mark.asyncio
    async def test_keeps_all_valid_links(self, sample_links: list[MarketplaceLink]):
        """Should keep all links that have results."""

        async def mock_validate(link: MarketplaceLink, timeout: float):
            return (link, True)  # All valid

        with patch("src.services.link_validator.validate_single_link", side_effect=mock_validate):
            result = await validate_marketplace_links(sample_links)

            assert len(result) == 3

    @pytest.mark.asyncio
    async def test_keeps_at_least_one_link(self, sample_links: list[MarketplaceLink]):
        """Should keep at least one link even if all fail validation."""

        async def mock_validate(link: MarketplaceLink, timeout: float):
            return (link, False)  # All fail

        with patch("src.services.link_validator.validate_single_link", side_effect=mock_validate):
            result = await validate_marketplace_links(sample_links)

            assert len(result) == 1  # At least one returned

    @pytest.mark.asyncio
    async def test_empty_input_returns_empty(self):
        """Should handle empty input gracefully."""
        result = await validate_marketplace_links([])

        assert result == []

    @pytest.mark.asyncio
    async def test_handles_exceptions_gracefully(self, sample_links: list[MarketplaceLink]):
        """Should handle exceptions and continue processing."""

        async def mock_validate(link: MarketplaceLink, timeout: float):
            if "2" in link.url:
                raise Exception("Unexpected error")
            return (link, True)

        with patch("src.services.link_validator.validate_single_link", side_effect=mock_validate):
            result = await validate_marketplace_links(sample_links)

            # Should have 2 results (links 1 and 3), exception for link 2 is handled
            assert len(result) == 2
