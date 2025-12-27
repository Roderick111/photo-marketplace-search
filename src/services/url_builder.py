"""
Marketplace URL builder service.

Builds search URLs for French marketplaces based on object type
and search queries from vision analysis.
"""

import logging
from urllib.parse import quote

from src.models.responses import MarketplaceLink, VisionAnalysisResult

logger = logging.getLogger(__name__)

# Marketplace URL templates
# {query} will be replaced with URL-encoded search query
MARKETPLACE_URLS: dict[str, tuple[str, str]] = {
    "book": (
        "abebooks",
        "https://www.abebooks.fr/servlet/SearchResults?kn={query}&sts=t",
    ),
    "clothing": (
        "vinted",
        "https://www.vinted.fr/catalog?search_text={query}",
    ),
}

# Default marketplace for categories not in MARKETPLACE_URLS
DEFAULT_MARKETPLACE: tuple[str, str] = (
    "leboncoin",
    "https://www.leboncoin.fr/recherche?text={query}",
)


def get_marketplace_for_type(
    object_type: str,
) -> tuple[str, str]:
    """
    Get marketplace name and URL template for object type.

    Args:
        object_type: Category from vision analysis.

    Returns:
        Tuple of (marketplace_name, url_template).
    """
    return MARKETPLACE_URLS.get(object_type, DEFAULT_MARKETPLACE)


def encode_query(query: str) -> str:
    """
    URL-encode search query for marketplace URLs.

    Args:
        query: Raw search query text.

    Returns:
        URL-encoded query string.
    """
    return quote(query, safe="")


def build_marketplace_link(
    marketplace_name: str,
    url_template: str,
    query: str,
) -> MarketplaceLink:
    """
    Build a single marketplace link.

    Args:
        marketplace_name: Name of the marketplace.
        url_template: URL template with {query} placeholder.
        query: Search query text.

    Returns:
        MarketplaceLink with encoded URL.
    """
    encoded_query = encode_query(query)
    url = url_template.format(query=encoded_query)

    return MarketplaceLink(
        marketplace=marketplace_name,  # type: ignore[arg-type]
        query=query,
        url=url,
    )


def build_marketplace_links(
    analysis: VisionAnalysisResult,
    max_links: int = 5,
) -> list[MarketplaceLink]:
    """
    Build marketplace search URLs based on analysis results.

    Routes to appropriate marketplace based on object type:
    - book -> Abebooks.fr
    - clothing -> Vinted
    - everything else -> Leboncoin

    Args:
        analysis: Vision analysis result with object type and queries.
        max_links: Maximum number of links to generate (default 5).

    Returns:
        List of MarketplaceLink objects with encoded URLs.
    """
    logger.info(f"Building links for object type: {analysis.object_type}")

    # Get marketplace for this object type
    marketplace_name, url_template = get_marketplace_for_type(analysis.object_type)

    # Build links for each search query
    links: list[MarketplaceLink] = []
    for search_query in analysis.search_queries[:max_links]:
        link = build_marketplace_link(
            marketplace_name=marketplace_name,
            url_template=url_template,
            query=search_query.query,
        )
        links.append(link)
        logger.debug(f"Generated link: {link.url}")

    logger.info(f"Generated {len(links)} marketplace links for {marketplace_name}")
    return links
