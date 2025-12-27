"""
Marketplace link validator service.

Validates marketplace URLs by checking if they return search results.
Filters out links with no results before returning to users.
"""

import asyncio
import logging

import httpx
from bs4 import BeautifulSoup

from src.models.responses import MarketplaceLink

logger = logging.getLogger(__name__)

# Marketplace-specific selectors for detecting results
MARKETPLACE_SELECTORS: dict[str, dict[str, list[str] | str]] = {
    "abebooks": {
        "no_results_text": ["aucun résultat", "no results found", "0 résultat"],
        "results_selector": ".result-item, .cf-search-results-content, #srp-results",
    },
    "vinted": {
        "no_results_text": ["aucun article", "aucun résultat"],
        "results_selector": ".feed-grid__item, .ItemBox_container, [data-testid='item-box']",
    },
    "leboncoin": {
        "no_results_text": ["aucune annonce", "0 annonce trouvée", "pas de résultat"],
        "results_selector": "[data-qa-id='aditem_container'], .styles_adCard, [data-test-id='ad']",
    },
}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def check_for_results(html: str, marketplace: str) -> bool:
    """
    Check if HTML contains search results for given marketplace.

    Args:
        html: Raw HTML string from marketplace.
        marketplace: Marketplace name (abebooks, vinted, leboncoin).

    Returns:
        True if results found, False if no results.
    """
    soup = BeautifulSoup(html, "lxml")
    selectors = MARKETPLACE_SELECTORS.get(marketplace, {})

    # Check for "no results" text (case-insensitive)
    page_text = soup.get_text().lower()
    no_results_phrases = selectors.get("no_results_text", [])
    if isinstance(no_results_phrases, list):
        for phrase in no_results_phrases:
            if phrase.lower() in page_text:
                logger.debug(f"Found no-results indicator: '{phrase}'")
                return False

    # Check for result items using CSS selector
    results_selector = selectors.get("results_selector", "")
    if results_selector and isinstance(results_selector, str):
        results = soup.select(results_selector)
        if len(results) > 0:
            logger.debug(f"Found {len(results)} result items")
            return True

    # Default: assume results exist if no negative indicator found
    return True


async def validate_single_link(
    link: MarketplaceLink,
    timeout: float = 3.0,
) -> tuple[MarketplaceLink, bool]:
    """
    Validate a single marketplace link by fetching and checking for results.

    Args:
        link: MarketplaceLink to validate.
        timeout: Request timeout in seconds.

    Returns:
        Tuple of (link, has_results).
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(link.url, headers=DEFAULT_HEADERS)
            response.raise_for_status()

            has_results = check_for_results(response.text, link.marketplace)
            logger.info(f"Validated {link.marketplace}: has_results={has_results}")
            return (link, has_results)

    except httpx.TimeoutException:
        logger.warning(f"Timeout validating {link.url}")
        return (link, True)  # On timeout, assume valid (fail open)

    except Exception as e:
        logger.warning(f"Error validating {link.url}: {e}")
        return (link, True)  # On error, assume valid (fail open)


async def validate_marketplace_links(
    links: list[MarketplaceLink],
    timeout: float = 3.0,
) -> list[MarketplaceLink]:
    """
    Validate multiple marketplace links in parallel.

    Filters out links with no results. Always returns at least one link.

    Args:
        links: List of MarketplaceLinks to validate.
        timeout: Request timeout per link.

    Returns:
        Filtered list with only links that have results.
    """
    if not links:
        return links

    logger.info(f"Validating {len(links)} marketplace links...")

    # Validate all links in parallel
    tasks = [validate_single_link(link, timeout) for link in links]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter to only links with results
    valid_links: list[MarketplaceLink] = []
    for result in results:
        if isinstance(result, BaseException):
            continue
        # result is tuple[MarketplaceLink, bool]
        link, has_results = result
        if has_results:
            valid_links.append(link)

    # CRITICAL: Always return at least one link
    if not valid_links and links:
        logger.warning("No valid links found, returning first link as fallback")
        valid_links = [links[0]]

    logger.info(f"Validation complete: {len(valid_links)}/{len(links)} links valid")
    return valid_links
