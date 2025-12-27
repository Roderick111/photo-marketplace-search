"""
Tests for the URL builder service.
"""

import pytest

from src.models.responses import SearchQuery, VisionAnalysisResult
from src.services.url_builder import (
    build_marketplace_link,
    build_marketplace_links,
    encode_query,
    get_marketplace_for_type,
)


class TestGetMarketplaceForType:
    """Tests for marketplace type routing."""

    def test_book_routes_to_abebooks(self) -> None:
        """Books should route to Abebooks."""
        name, url = get_marketplace_for_type("book")
        assert name == "abebooks"
        assert "abebooks.fr" in url

    def test_clothing_routes_to_vinted(self) -> None:
        """Clothing should route to Vinted."""
        name, url = get_marketplace_for_type("clothing")
        assert name == "vinted"
        assert "vinted.fr" in url

    @pytest.mark.parametrize(
        "object_type",
        ["electronics", "furniture", "tools", "general", "unknown"],
    )
    def test_other_types_route_to_leboncoin(self, object_type: str) -> None:
        """Other types should default to Leboncoin."""
        name, url = get_marketplace_for_type(object_type)
        assert name == "leboncoin"
        assert "leboncoin.fr" in url


class TestEncodeQuery:
    """Tests for URL query encoding."""

    def test_simple_query(self) -> None:
        """Simple query should be encoded."""
        result = encode_query("livre")
        assert result == "livre"

    def test_query_with_spaces(self) -> None:
        """Spaces should be encoded."""
        result = encode_query("roman policier")
        assert result == "roman%20policier"

    def test_query_with_accents(self) -> None:
        """French accents should be encoded."""
        result = encode_query("clé à molette")
        assert "cl%C3%A9" in result  # é
        assert "%C3%A0" in result  # à

    def test_query_with_special_chars(self) -> None:
        """Special characters should be encoded."""
        result = encode_query("t-shirt & jeans")
        assert "%26" in result  # &


class TestBuildMarketplaceLink:
    """Tests for building individual marketplace links."""

    def test_builds_correct_url(self) -> None:
        """Should build correct marketplace URL."""
        link = build_marketplace_link(
            marketplace_name="abebooks",
            url_template="https://www.abebooks.fr/servlet/SearchResults?kn={query}&sts=t",
            query="livre policier",
        )
        assert link.marketplace == "abebooks"
        assert link.query == "livre policier"
        assert "livre%20policier" in link.url
        assert "abebooks.fr" in link.url


class TestBuildMarketplaceLinks:
    """Tests for building multiple marketplace links."""

    def test_builds_links_for_book(self) -> None:
        """Should build Abebooks links for books."""
        analysis = VisionAnalysisResult(
            object_type="book",
            description="Roman policier",
            search_queries=[
                SearchQuery(query="roman policier", confidence=0.9),
                SearchQuery(query="thriller français", confidence=0.85),
            ],
            confidence=0.88,
        )

        links = build_marketplace_links(analysis)

        assert len(links) == 2
        for link in links:
            assert link.marketplace == "abebooks"
            assert "abebooks.fr" in link.url

    def test_builds_links_for_clothing(self) -> None:
        """Should build Vinted links for clothing."""
        analysis = VisionAnalysisResult(
            object_type="clothing",
            description="T-shirt noir",
            search_queries=[SearchQuery(query="tshirt noir", confidence=0.9)],
            confidence=0.9,
        )

        links = build_marketplace_links(analysis)

        assert len(links) == 1
        assert links[0].marketplace == "vinted"
        assert "vinted.fr" in links[0].url

    def test_builds_links_for_electronics(self) -> None:
        """Should build Leboncoin links for electronics."""
        analysis = VisionAnalysisResult(
            object_type="electronics",
            description="Smartphone",
            search_queries=[SearchQuery(query="telephone portable", confidence=0.85)],
            confidence=0.8,
        )

        links = build_marketplace_links(analysis)

        assert len(links) == 1
        assert links[0].marketplace == "leboncoin"
        assert "leboncoin.fr" in links[0].url

    def test_respects_max_links(self) -> None:
        """Should not exceed max_links parameter."""
        analysis = VisionAnalysisResult(
            object_type="general",
            description="Various items",
            search_queries=[
                SearchQuery(query="query1", confidence=0.9),
                SearchQuery(query="query2", confidence=0.85),
                SearchQuery(query="query3", confidence=0.8),
            ],
            confidence=0.85,
        )

        links = build_marketplace_links(analysis, max_links=2)

        assert len(links) == 2

    def test_handles_french_special_characters(self) -> None:
        """Should properly encode French special characters in URLs."""
        analysis = VisionAnalysisResult(
            object_type="book",
            description="Book with special chars",
            search_queries=[
                SearchQuery(query="clé à molette 20mm", confidence=0.8),
            ],
            confidence=0.75,
        )

        links = build_marketplace_links(analysis)

        # Verify URL encoding
        assert "cl%C3%A9" in links[0].url  # é encoded
        assert "%C3%A0" in links[0].url  # à encoded
