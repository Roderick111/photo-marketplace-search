name: "Marketplace Link Validation - Filter Empty Results"
description: |

## Purpose
Add validation to marketplace links before returning them to users. Check if each marketplace search URL actually has results - if a search returns no products, don't include that link in the response.

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Follow all rules in CLAUDE.md

---

## Goal
Create an async link validation service that checks marketplace URLs for actual search results before returning them to users. Links with no results should be filtered out.

## Why
- **User Experience**: Users waste time clicking links that have no products
- **Trust**: Returning empty search links damages app credibility
- **Efficiency**: Show only actionable results

## What
When marketplace links are generated, validate each by:
1. Making an async HTTP GET request to the URL
2. Parsing the HTML response with BeautifulSoup
3. Checking for "no results" indicators specific to each marketplace
4. Filtering out links that have no results
5. If ALL links have no results, return at least one with lowest confidence (fallback)

### Success Criteria
- [ ] Links with no marketplace results are filtered out
- [ ] Validation runs in parallel for performance (< 3 seconds total)
- [ ] Graceful fallback if validation fails (return link anyway)
- [ ] At least one link always returned (never empty response)
- [ ] All tests pass with mocked HTTP responses
- [ ] Type checking passes with mypy

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://www.python-httpx.org/async/
  why: AsyncClient usage pattern for making async HTTP requests

- url: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
  why: HTML parsing with find() and find_all() methods
  critical: "find() returns None if element not found - always check before use"

- file: photo-marketplace-search/src/services/url_builder.py
  why: Current link generation pattern, MarketplaceLink model usage

- file: photo-marketplace-search/src/services/vision_service.py
  why: Pattern for async service with error handling and logging

- file: photo-marketplace-search/src/api/routes.py
  why: Integration point - where to call validator after build_marketplace_links()

- file: photo-marketplace-search/src/tests/test_url_builder.py
  why: Test patterns for services
```

### Current Codebase Tree
```bash
photo-marketplace-search/
├── src/
│   ├── api/
│   │   └── routes.py          # Integration point
│   ├── core/
│   │   ├── config.py          # Add LINK_VALIDATION_TIMEOUT
│   │   └── exceptions.py      # Add LinkValidationError (optional)
│   ├── models/
│   │   └── responses.py       # MarketplaceLink model
│   ├── services/
│   │   ├── url_builder.py     # Current link building
│   │   ├── vision_service.py  # Pattern reference
│   │   └── link_validator.py  # NEW FILE
│   └── tests/
│       └── test_link_validator.py  # NEW FILE
└── pyproject.toml             # Add beautifulsoup4, httpx deps
```

### Desired Codebase Tree with New Files
```bash
photo-marketplace-search/src/services/link_validator.py
  - MARKETPLACE_SELECTORS dict with CSS selectors per marketplace
  - validate_single_link() - async function to check one URL
  - validate_marketplace_links() - async function to validate all links in parallel

photo-marketplace-search/src/tests/test_link_validator.py
  - Tests with mocked HTTP responses
  - Test no-results detection per marketplace
  - Test fallback behavior
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: httpx requires explicit timeout or it hangs on slow sites
async with httpx.AsyncClient(timeout=3.0) as client:
    response = await client.get(url)

# CRITICAL: BeautifulSoup find() returns None, not empty - must check
result = soup.find('div', class_='no-results')
if result is not None:  # NOT just "if result:"
    # Element exists

# CRITICAL: Marketplaces may block requests without User-Agent
headers = {"User-Agent": "Mozilla/5.0 (compatible; PhotoSearch/1.0)"}

# CRITICAL: Use asyncio.gather with return_exceptions=True for parallel requests
results = await asyncio.gather(*tasks, return_exceptions=True)

# GOTCHA: Some marketplaces use JavaScript rendering - basic HTTP won't work
# For now, only validate marketplaces that work with server-side HTML
```

## Implementation Blueprint

### Data Models
```python
# No new models needed - use existing MarketplaceLink from responses.py
# Optionally add to responses.py:
class ValidatedMarketplaceLink(MarketplaceLink):
    """MarketplaceLink with validation status."""
    has_results: bool = True  # Only if we want to expose this to frontend
```

### Marketplace Selectors Configuration
```python
# Each marketplace has different "no results" indicators
MARKETPLACE_SELECTORS: dict[str, dict[str, str | list[str]]] = {
    "abebooks": {
        # Abebooks shows "Aucun résultat" or specific class when no results
        "no_results_text": ["Aucun résultat", "no results", "0 résultat"],
        "results_selector": ".result-item, .book-item, [data-ref='result-item']",
    },
    "vinted": {
        # Vinted shows empty state with specific text
        "no_results_text": ["Aucun article", "Aucun résultat"],
        "results_selector": ".feed-grid__item, [data-testid='item-grid']",
    },
    "leboncoin": {
        # Leboncoin shows empty state
        "no_results_text": ["Aucune annonce", "0 annonce"],
        "results_selector": "[data-qa-id='aditem_container'], .ad-item",
    },
}
```

### Task List

```yaml
Task 1: Add dependencies
  MODIFY pyproject.toml:
    - ADD: "beautifulsoup4>=4.12.0" to dependencies
    - ADD: "lxml>=5.0.0" to dependencies (faster parser)
    - NOTE: httpx already exists in dev dependencies, move to main if needed

Task 2: Add config setting
  MODIFY src/core/config.py:
    - ADD: link_validation_timeout: int = Field(default=3)
    - ADD: link_validation_enabled: bool = Field(default=True)

Task 3: Create link validator service
  CREATE src/services/link_validator.py:
    - IMPORT: httpx, asyncio, BeautifulSoup, logging
    - DEFINE: MARKETPLACE_SELECTORS constant
    - IMPLEMENT: check_for_results(html: str, marketplace: str) -> bool
    - IMPLEMENT: validate_single_link(link: MarketplaceLink, timeout: float) -> tuple[MarketplaceLink, bool]
    - IMPLEMENT: validate_marketplace_links(links: list[MarketplaceLink], timeout: float) -> list[MarketplaceLink]

Task 4: Integrate validator into routes
  MODIFY src/api/routes.py:
    - IMPORT: from src.services import link_validator
    - AFTER line "links = url_builder.build_marketplace_links(analysis)"
    - ADD: links = await link_validator.validate_marketplace_links(links, settings.link_validation_timeout)

Task 5: Create unit tests
  CREATE src/tests/test_link_validator.py:
    - TEST: test_check_for_results_abebooks_with_results
    - TEST: test_check_for_results_abebooks_no_results
    - TEST: test_check_for_results_vinted_with_results
    - TEST: test_check_for_results_vinted_no_results
    - TEST: test_validate_single_link_success
    - TEST: test_validate_single_link_timeout
    - TEST: test_validate_marketplace_links_filters_empty
    - TEST: test_validate_marketplace_links_keeps_at_least_one

Task 6: Run validation and fix issues
  RUN: uv run ruff check --fix src/services/link_validator.py
  RUN: uv run mypy src/services/link_validator.py
  RUN: uv run pytest src/tests/test_link_validator.py -v
```

### Task 3 Pseudocode - Link Validator Service
```python
"""
Marketplace link validator service.

Validates marketplace URLs by checking if they return search results.
"""

import asyncio
import logging
from bs4 import BeautifulSoup
import httpx

from src.models.responses import MarketplaceLink

logger = logging.getLogger(__name__)

# CRITICAL: Define selectors for each marketplace
MARKETPLACE_SELECTORS: dict[str, dict] = {
    "abebooks": {
        "no_results_text": ["aucun résultat", "no results found", "0 résultat"],
        "results_selector": ".result-item, .cf-search-results-content",
    },
    "vinted": {
        "no_results_text": ["aucun article", "aucun résultat"],
        "results_selector": ".feed-grid__item, .ItemBox_container",
    },
    "leboncoin": {
        "no_results_text": ["aucune annonce", "0 annonce trouvée"],
        "results_selector": "[data-qa-id='aditem_container'], .styles_adCard",
    },
}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def check_for_results(html: str, marketplace: str) -> bool:
    """
    Check if HTML contains search results for given marketplace.

    Args:
        html: Raw HTML string from marketplace
        marketplace: Marketplace name (abebooks, vinted, leboncoin)

    Returns:
        True if results found, False if no results
    """
    soup = BeautifulSoup(html, "lxml")
    selectors = MARKETPLACE_SELECTORS.get(marketplace, {})

    # Check for "no results" text (case-insensitive)
    page_text = soup.get_text().lower()
    no_results_phrases = selectors.get("no_results_text", [])
    for phrase in no_results_phrases:
        if phrase.lower() in page_text:
            logger.debug(f"Found no-results indicator: '{phrase}'")
            return False

    # Check for result items using CSS selector
    results_selector = selectors.get("results_selector", "")
    if results_selector:
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
        link: MarketplaceLink to validate
        timeout: Request timeout in seconds

    Returns:
        Tuple of (link, has_results)
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
        links: List of MarketplaceLinks to validate
        timeout: Request timeout per link

    Returns:
        Filtered list with only links that have results
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
        if isinstance(result, Exception):
            continue
        link, has_results = result
        if has_results:
            valid_links.append(link)

    # CRITICAL: Always return at least one link
    if not valid_links and links:
        logger.warning("No valid links found, returning first link as fallback")
        valid_links = [links[0]]

    logger.info(f"Validation complete: {len(valid_links)}/{len(links)} links valid")
    return valid_links
```

### Integration Points
```yaml
DEPENDENCIES:
  - modify: pyproject.toml
  - add: "beautifulsoup4>=4.12.0"
  - add: "lxml>=5.0.0"
  - run: uv sync

CONFIG:
  - modify: src/core/config.py
  - add: link_validation_timeout: int = Field(default=3)
  - add: link_validation_enabled: bool = Field(default=True)

ROUTES:
  - modify: src/api/routes.py
  - after: links = url_builder.build_marketplace_links(analysis)
  - add: |
      if settings.link_validation_enabled:
          links = await link_validator.validate_marketplace_links(
              links, settings.link_validation_timeout
          )
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
cd /Users/danielmedina/Documents/claude_projects/context-engineering-intro/photo-marketplace-search

uv sync  # Install new dependencies
uv run ruff check src/services/link_validator.py --fix
uv run ruff format src/services/link_validator.py
uv run mypy src/services/link_validator.py

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests
```python
# CREATE src/tests/test_link_validator.py with these test cases:

import pytest
from unittest.mock import patch, AsyncMock
from src.services.link_validator import (
    check_for_results,
    validate_single_link,
    validate_marketplace_links,
)
from src.models.responses import MarketplaceLink


class TestCheckForResults:
    """Tests for HTML result detection."""

    def test_abebooks_with_results(self):
        """Should detect results when product items present."""
        html = '''
        <html><body>
            <div class="result-item">Book 1</div>
            <div class="result-item">Book 2</div>
        </body></html>
        '''
        assert check_for_results(html, "abebooks") is True

    def test_abebooks_no_results(self):
        """Should detect no results from text indicator."""
        html = '''
        <html><body>
            <p>Aucun résultat trouvé pour votre recherche</p>
        </body></html>
        '''
        assert check_for_results(html, "abebooks") is False

    def test_vinted_with_results(self):
        """Should detect Vinted results."""
        html = '<div class="feed-grid__item">Item</div>'
        assert check_for_results(html, "vinted") is True

    def test_vinted_no_results(self):
        """Should detect no Vinted results."""
        html = '<p>Aucun article correspondant</p>'
        assert check_for_results(html, "vinted") is False

    def test_unknown_marketplace_defaults_true(self):
        """Unknown marketplace should default to having results."""
        html = '<html><body>Some content</body></html>'
        assert check_for_results(html, "unknown") is True


class TestValidateSingleLink:
    """Tests for single link validation."""

    @pytest.fixture
    def sample_link(self) -> MarketplaceLink:
        return MarketplaceLink(
            marketplace="abebooks",
            query="livre test",
            url="https://www.abebooks.fr/servlet/SearchResults?kn=livre%20test",
        )

    @pytest.mark.asyncio
    async def test_validates_link_with_results(self, sample_link):
        """Should return True for link with results."""
        mock_html = '<div class="result-item">Book</div>'

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = AsyncMock()
            mock_response.text = mock_html
            mock_response.raise_for_status = lambda: None

            mock_instance = AsyncMock()
            mock_instance.get.return_value = mock_response
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            link, has_results = await validate_single_link(sample_link)
            assert has_results is True

    @pytest.mark.asyncio
    async def test_timeout_returns_true(self, sample_link):
        """Should return True (fail open) on timeout."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = httpx.TimeoutException("Timeout")
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.__aexit__.return_value = None
            mock_client.return_value = mock_instance

            link, has_results = await validate_single_link(sample_link)
            assert has_results is True  # Fail open


class TestValidateMarketplaceLinks:
    """Tests for bulk link validation."""

    @pytest.fixture
    def sample_links(self) -> list[MarketplaceLink]:
        return [
            MarketplaceLink(marketplace="abebooks", query="book1", url="https://example.com/1"),
            MarketplaceLink(marketplace="abebooks", query="book2", url="https://example.com/2"),
            MarketplaceLink(marketplace="abebooks", query="book3", url="https://example.com/3"),
        ]

    @pytest.mark.asyncio
    async def test_filters_empty_results(self, sample_links):
        """Should filter out links with no results."""
        # Mock: first has results, second and third don't
        async def mock_validate(link, timeout):
            if "1" in link.url:
                return (link, True)
            return (link, False)

        with patch("src.services.link_validator.validate_single_link", side_effect=mock_validate):
            result = await validate_marketplace_links(sample_links)
            assert len(result) == 1
            assert "1" in result[0].url

    @pytest.mark.asyncio
    async def test_keeps_at_least_one_link(self, sample_links):
        """Should keep at least one link even if all fail validation."""
        async def mock_validate(link, timeout):
            return (link, False)  # All fail

        with patch("src.services.link_validator.validate_single_link", side_effect=mock_validate):
            result = await validate_marketplace_links(sample_links)
            assert len(result) == 1  # At least one returned

    @pytest.mark.asyncio
    async def test_empty_input_returns_empty(self):
        """Should handle empty input gracefully."""
        result = await validate_marketplace_links([])
        assert result == []
```

```bash
# Run tests and iterate until passing:
uv run pytest src/tests/test_link_validator.py -v

# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start the service
uv run uvicorn src.main:app --reload --port 8000

# Test with a real image upload through the web interface
# Check that links returned actually have results on the marketplace

# Or test API directly:
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_image.jpg"

# Expected: Only links with actual marketplace results
```

## Final Validation Checklist
- [ ] Dependencies installed: `uv sync`
- [ ] All tests pass: `uv run pytest src/tests/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Manual test successful: Upload image, verify returned links have results
- [ ] Error cases handled gracefully (timeouts fail open)
- [ ] Logs are informative but not verbose
- [ ] At least one link always returned

---

## Anti-Patterns to Avoid
- ❌ Don't block on validation forever - use timeout
- ❌ Don't return empty list - always have fallback
- ❌ Don't ignore exceptions - log and fail open
- ❌ Don't make sequential requests - use asyncio.gather
- ❌ Don't hardcode timeouts - use config
- ❌ Don't skip User-Agent header - may get blocked

---

## Confidence Score: 8/10

**Rationale:**
- (+) Clear implementation pattern with good examples
- (+) Follows existing codebase conventions
- (+) Comprehensive test cases provided
- (+) Error handling strategy defined (fail open)
- (-) Marketplace HTML structure may change (selectors might need adjustment)
- (-) Some marketplaces use JavaScript rendering (may not work with httpx)
- (-) Rate limiting concerns if many requests

**Mitigation:** The fail-open strategy ensures the feature degrades gracefully. Selectors can be adjusted after testing with real marketplace pages.
