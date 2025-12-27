name: "Gem Finder - Marketplace Product Analysis & Ranking"
description: |

## Purpose
Build a "Gem Finder" feature that analyzes marketplace listings to find the best quality-to-price items. Takes links from Feature 1 (photo search), scrapes products, generates dynamic evaluation criteria via Claude AI, and ranks items with tiered recommendations.

## Core Principles
1. **Keep It Simple**: One scraper file using Playwright - works on all marketplaces
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Graceful Degradation**: Scraping may fail - handle gracefully
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Follow all rules in CLAUDE.md

---

## Goal
Create a complete gem finder system that:
1. Imports marketplace links from Feature 1 or accepts manual input
2. Scrapes product data from Vinted, Leboncoin, and Abebooks using Playwright
3. Uses Claude AI to generate dynamic evaluation criteria based on product type
4. Ranks products by quality-to-price ratio
5. Provides tiered recommendations (Entry/Mid/High) and CSV export

## Why
- **User Value**: Find best deals without manually comparing 50+ listings
- **Time Savings**: Automated analysis vs hours of manual comparison
- **Data-Driven Decisions**: Objective scoring based on relevant criteria
- **Integration**: Natural extension of photo-to-search Feature 1

## What
### User Flow
1. User imports links from Feature 1 or pastes marketplace URLs
2. User edits link list (add/remove URLs)
3. Click "Find Gems" → Scraping begins with progress indicator
4. Claude analyzes product category and generates 2-3 evaluation criteria
5. Products are scored and ranked
6. Display: Top 3-5 recommendations by tier (if applicable)
7. Download: Complete CSV with all products and scores

### Success Criteria
- [ ] Can import links from Feature 1 response
- [ ] Can manually add/remove URLs
- [ ] Scrapes products using Playwright (real browser)
- [ ] Claude generates relevant criteria based on product type
- [ ] Products ranked by quality-to-price score
- [ ] Tiered recommendations displayed (Entry/Mid/High when relevant)
- [ ] CSV export with all products and scores
- [ ] Progress indicators during scraping
- [ ] Graceful error handling (some URLs may fail)
- [ ] All tests pass

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Critical for implementation
- url: https://playwright.dev/python/docs/intro
  why: Primary scraping tool - real browser automation
  critical: "Use async API, headless mode for production"

- url: https://playwright.dev/python/docs/api/class-page#page-evaluate
  why: Extract data from page using JavaScript evaluation
  critical: "Best way to extract structured data from DOM"

- url: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
  why: CSV export with proper encoding for French characters

- url: https://docs.anthropic.com/en/docs/build-with-claude/tool-use
  why: Claude structured outputs for criteria generation

- file: photo-marketplace-search/src/services/vision_service.py
  why: Pattern for Claude API integration with structured JSON output

- file: photo-marketplace-search/src/models/responses.py
  why: Existing MarketplaceLink model to extend

- file: photo-marketplace-search/src/tests/test_link_validator.py
  why: Test patterns with mocked responses
```

### Current Codebase Tree (Simplified)
```bash
photo-marketplace-search/
├── src/
│   ├── api/routes.py              # Add new gem finder endpoints
│   ├── core/config.py             # Add scraping config
│   ├── models/
│   │   ├── responses.py           # Existing MarketplaceLink
│   │   └── gem_finder.py          # NEW: Product, Criteria, Result models
│   ├── services/
│   │   ├── vision_service.py      # Pattern reference
│   │   ├── scraper.py             # NEW: Single Playwright scraper (ONE FILE)
│   │   ├── criteria_service.py    # NEW: Claude criteria generation
│   │   └── analysis_service.py    # NEW: Scoring and ranking
│   ├── static/
│   │   ├── gem_finder.html        # NEW: Gem finder page
│   │   └── gem_finder.js          # NEW: Gem finder JavaScript
│   └── tests/
│       └── test_gem_finder.py     # NEW: All gem finder tests
└── pyproject.toml                 # Add pandas, playwright
```

### Why Playwright Instead of httpx/vinted-scraper

| Approach | Files | Lines | Leboncoin Works? | Complexity |
|----------|-------|-------|------------------|------------|
| Old (httpx + vinted-scraper) | 5 | ~300 | No (DataDome blocks) | High |
| New (Playwright) | 1 | ~80 | Maybe (real browser) | Low |

**Playwright advantages:**
- Real browser = harder for anti-bot to detect
- One unified approach for all marketplaces
- Simple CSS selectors to extract data
- No need for stealth headers, TLS fingerprinting hacks

### Known Gotchas & Library Quirks
```python
# CRITICAL: Install Playwright browsers after adding dependency
# RUN: playwright install chromium

# CRITICAL: Use headless=True for production, False for debugging
browser = await p.chromium.launch(headless=True)

# CRITICAL: Wait for content to load before extracting
await page.wait_for_load_state("networkidle")
# Or wait for specific selector:
await page.wait_for_selector(".product-card", timeout=10000)

# CRITICAL: Price normalization for French format
# "49,99 €" → 49.99
import re
def normalize_price(price_str: str) -> float | None:
    if not price_str:
        return None
    cleaned = re.sub(r'[€$\s]', '', price_str)
    cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return None

# CRITICAL: Rate limiting - add delays between pages
import asyncio
await asyncio.sleep(2)  # 2 seconds between requests

# GOTCHA: Selectors vary by marketplace - use fallbacks
selectors = {
    "vinted": ".feed-grid__item, .new-item-box__container",
    "leboncoin": "[data-test-id='adcard'], .aditem_container",
    "abebooks": ".result-item, .srp-item-image",
}
```

## Implementation Blueprint

### Data Models (src/models/gem_finder.py)
```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class ScrapedProduct(BaseModel):
    """Raw product data from marketplace scraping."""
    marketplace: str
    title: str
    price: float | None = None
    url: str
    description: str | None = None
    condition: str | None = None
    image_url: str | None = None
    scraped_at: datetime = Field(default_factory=datetime.now)

class EvaluationCriterion(BaseModel):
    """Single evaluation criterion generated by Claude."""
    name: str = Field(..., description="Criterion name, e.g., 'Brand Reputation'")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight 0-1")
    description: str = Field(..., description="How to evaluate this criterion")

class CriteriaSet(BaseModel):
    """Set of criteria for product evaluation."""
    product_category: str
    criteria: list[EvaluationCriterion] = Field(..., min_length=1, max_length=3)
    reasoning: str

class ScoredProduct(BaseModel):
    """Product with computed quality scores."""
    product: ScrapedProduct
    criteria_scores: dict[str, float]  # criterion_name -> score 0-100
    overall_score: float
    tier: Literal["entry", "mid", "high", "none"] | None = None
    recommendation_rank: int | None = None

class GemFinderRequest(BaseModel):
    """Request to find gems from marketplace links."""
    urls: list[str] = Field(..., min_length=1)

class GemFinderResponse(BaseModel):
    """Complete gem finder results."""
    total_products_found: int
    total_products_scored: int
    criteria_used: CriteriaSet
    recommendations: list[ScoredProduct]
    all_products: list[ScoredProduct]
    scraping_errors: list[str]
    processing_time_seconds: float
```

### Task List

```yaml
Task 1: Add dependencies
  MODIFY pyproject.toml:
    - ADD: "pandas>=2.0.0" to dependencies
    - ADD: "playwright>=1.40.0" to dependencies
  RUN: uv sync
  RUN: playwright install chromium

Task 2: Create data models
  CREATE src/models/gem_finder.py:
    - ScrapedProduct, EvaluationCriterion, CriteriaSet
    - ScoredProduct, GemFinderRequest, GemFinderResponse

Task 3: Add config settings
  MODIFY src/core/config.py:
    - ADD: scraping_delay_seconds: float = Field(default=2.0)
    - ADD: max_products_per_url: int = Field(default=50)
    - ADD: scraping_timeout_ms: int = Field(default=30000)
    - ADD: headless_browser: bool = Field(default=True)

Task 4: Create Playwright scraper (SINGLE FILE)
  CREATE src/services/scraper.py:
    - scrape_url(url: str) -> list[ScrapedProduct]
    - detect_marketplace(url: str) -> str
    - Marketplace-specific CSS selectors
    - Graceful error handling

Task 5: Create criteria service
  CREATE src/services/criteria_service.py:
    - generate_criteria(products: list[ScrapedProduct]) -> CriteriaSet
    - Use Claude API with structured output
    - Fallback criteria if Claude fails

Task 6: Create analysis service
  CREATE src/services/analysis_service.py:
    - score_products(products, criteria) -> list[ScoredProduct]
    - assign_tiers(products) -> list[ScoredProduct]
    - get_recommendations(products, top_n=5) -> list[ScoredProduct]
    - export_csv(products) -> bytes

Task 7: Create gem finder endpoint
  MODIFY src/api/routes.py:
    - POST /api/gems - Main gem finder endpoint
    - GET /api/gems/csv - Download CSV

Task 8: Create frontend
  CREATE src/static/gem_finder.html
  CREATE src/static/gem_finder.js
    - Link input textarea
    - Progress indicator
    - Results display with tiers
    - CSV download button

Task 9: Create tests
  CREATE src/tests/test_gem_finder.py
    - Test models, scraper, criteria, analysis

Task 10: Run validation
  RUN: uv run ruff format . && uv run ruff check --fix .
  RUN: uv run mypy src/
  RUN: uv run pytest src/tests/ -v
```

### Task 4 - Playwright Scraper (THE KEY SIMPLIFICATION)
```python
"""
Unified marketplace scraper using Playwright.
ONE file, works on all marketplaces.
"""
import asyncio
import logging
import re
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Page

from src.core.config import get_settings
from src.models.gem_finder import ScrapedProduct

logger = logging.getLogger(__name__)

# Marketplace-specific selectors (fallback chain)
SELECTORS = {
    "vinted": {
        "container": ".feed-grid__item, .new-item-box__container, [data-testid='grid-item']",
        "title": ".new-item-box__title, .item-title, h3",
        "price": ".new-item-box__price, .item-price, [data-testid='price']",
        "link": "a",
        "image": "img",
    },
    "leboncoin": {
        "container": "[data-test-id='ad'], .aditem_container, article",
        "title": "[data-test-id='ad-subject'], .aditem_title, h2",
        "price": "[data-test-id='price'], .aditem_price, .price",
        "link": "a",
        "image": "img",
    },
    "abebooks": {
        "container": ".result-item, .srp-item",
        "title": ".title, h2 a",
        "price": ".item-price, .srp-item-price",
        "link": "a.title, h2 a",
        "image": "img",
    },
}


def detect_marketplace(url: str) -> str:
    """Detect marketplace from URL."""
    domain = urlparse(url).netloc.lower()
    if "vinted" in domain:
        return "vinted"
    elif "leboncoin" in domain:
        return "leboncoin"
    elif "abebooks" in domain:
        return "abebooks"
    return "unknown"


def normalize_price(price_str: str | None) -> float | None:
    """Normalize price string to float. Handles French format."""
    if not price_str:
        return None
    cleaned = re.sub(r'[€$£\s\u202f]', '', price_str)
    cleaned = cleaned.replace(',', '.').replace('\xa0', '')
    try:
        return float(cleaned)
    except ValueError:
        return None


async def extract_products(page: Page, marketplace: str) -> list[dict]:
    """Extract product data from page using JavaScript."""
    selectors = SELECTORS.get(marketplace, SELECTORS["vinted"])

    return await page.evaluate(
        """
        (selectors) => {
            const items = document.querySelectorAll(selectors.container);
            return Array.from(items).slice(0, 50).map(el => ({
                title: el.querySelector(selectors.title)?.textContent?.trim() || '',
                price: el.querySelector(selectors.price)?.textContent?.trim() || '',
                url: el.querySelector(selectors.link)?.href || '',
                image: el.querySelector(selectors.image)?.src || '',
            }));
        }
        """,
        selectors,
    )


async def scrape_url(url: str) -> list[ScrapedProduct]:
    """
    Scrape products from a marketplace URL using Playwright.
    Returns empty list on failure (graceful degradation).
    """
    settings = get_settings()
    marketplace = detect_marketplace(url)

    if marketplace == "unknown":
        logger.warning(f"Unknown marketplace for URL: {url}")
        return []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=settings.headless_browser)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Navigate and wait for content
            await page.goto(url, wait_until="networkidle", timeout=settings.scraping_timeout_ms)

            # Wait for product cards to appear
            selectors = SELECTORS.get(marketplace, SELECTORS["vinted"])
            try:
                await page.wait_for_selector(
                    selectors["container"],
                    timeout=10000
                )
            except Exception:
                logger.warning(f"No products found on page: {url}")
                await browser.close()
                return []

            # Extract products
            raw_products = await extract_products(page, marketplace)
            await browser.close()

            # Convert to ScrapedProduct models
            products = []
            for item in raw_products:
                if not item.get("title"):
                    continue
                products.append(
                    ScrapedProduct(
                        marketplace=marketplace,
                        title=item["title"],
                        price=normalize_price(item.get("price")),
                        url=item.get("url") or url,
                        image_url=item.get("image"),
                    )
                )

            logger.info(f"Scraped {len(products)} products from {marketplace}")
            return products

    except Exception as e:
        logger.error(f"Scraping failed for {url}: {e}")
        return []  # Graceful fallback


async def scrape_urls(urls: list[str], delay: float = 2.0) -> tuple[list[ScrapedProduct], list[str]]:
    """
    Scrape multiple URLs with delay between requests.
    Returns (products, failed_urls).
    """
    all_products = []
    failed_urls = []

    for url in urls:
        products = await scrape_url(url)
        if products:
            all_products.extend(products)
        else:
            failed_urls.append(url)

        # Rate limiting
        if url != urls[-1]:
            await asyncio.sleep(delay)

    return all_products, failed_urls
```

### Task 5 - Criteria Service
```python
"""Claude-powered criteria generation service."""

import json
import logging

import anthropic

from src.core.config import Settings
from src.models.gem_finder import CriteriaSet, EvaluationCriterion, ScrapedProduct

logger = logging.getLogger(__name__)

DEFAULT_CRITERIA = [
    EvaluationCriterion(name="Condition", weight=0.4, description="Item condition"),
    EvaluationCriterion(name="Price Value", weight=0.4, description="Price competitiveness"),
    EvaluationCriterion(name="Seller Rating", weight=0.2, description="Seller reliability"),
]


def _build_criteria_prompt(products: list[ScrapedProduct]) -> str:
    """Build prompt for Claude to generate criteria."""
    sample_titles = [p.title for p in products[:10]]
    sample_prices = [p.price for p in products[:10] if p.price]

    price_range = ""
    if sample_prices:
        price_range = f"Price range: {min(sample_prices):.2f}€ - {max(sample_prices):.2f}€"

    schema = CriteriaSet.model_json_schema()

    return f"""Analyze these marketplace product listings and generate evaluation criteria.

Sample product titles:
{json.dumps(sample_titles, indent=2, ensure_ascii=False)}

{price_range}

Your task:
1. Determine the product category (e.g., "book", "electronics", "clothing")
2. Generate 2-3 evaluation criteria that matter most for this category
3. Assign weights to each criterion (must sum to 1.0)

Return ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}"""


async def generate_criteria(
    products: list[ScrapedProduct],
    settings: Settings,
) -> CriteriaSet:
    """Generate evaluation criteria using Claude AI."""
    if not products:
        return CriteriaSet(
            product_category="general",
            criteria=DEFAULT_CRITERIA,
            reasoning="No products to analyze, using default criteria",
        )

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        prompt = _build_criteria_prompt(products)

        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text
        criteria = CriteriaSet.model_validate_json(response_text)
        logger.info(f"Generated criteria for category: {criteria.product_category}")
        return criteria

    except Exception as e:
        logger.error(f"Criteria generation failed: {e}")
        return CriteriaSet(
            product_category="general",
            criteria=DEFAULT_CRITERIA,
            reasoning=f"Claude API failed ({e}), using default criteria",
        )
```

### Task 6 - Analysis Service
```python
"""Product analysis and ranking service."""

import io
import logging

import pandas as pd

from src.models.gem_finder import CriteriaSet, ScoredProduct, ScrapedProduct

logger = logging.getLogger(__name__)


def score_product(product: ScrapedProduct, criteria: CriteriaSet) -> dict[str, float]:
    """Score a single product against criteria."""
    scores = {}
    for criterion in criteria.criteria:
        # Simplified scoring - can be enhanced with Claude scoring
        scores[criterion.name] = 70.0  # Base score
    return scores


def calculate_overall_score(scores: dict[str, float], criteria: CriteriaSet) -> float:
    """Calculate weighted overall score."""
    total = sum(
        scores.get(c.name, 0) * c.weight
        for c in criteria.criteria
    )
    return round(total, 2)


def score_products(
    products: list[ScrapedProduct],
    criteria: CriteriaSet,
) -> list[ScoredProduct]:
    """Score all products and return ScoredProduct list."""
    scored = []
    for product in products:
        scores = score_product(product, criteria)
        overall = calculate_overall_score(scores, criteria)
        scored.append(
            ScoredProduct(
                product=product,
                criteria_scores=scores,
                overall_score=overall,
            )
        )
    return scored


def assign_tiers(products: list[ScoredProduct]) -> list[ScoredProduct]:
    """Assign price tiers to products."""
    if not products:
        return products

    prices = [p.product.price for p in products if p.product.price]
    if not prices:
        for p in products:
            p.tier = "none"
        return products

    low = pd.Series(prices).quantile(0.33)
    high = pd.Series(prices).quantile(0.66)

    for product in products:
        price = product.product.price
        if price is None:
            product.tier = "none"
        elif price <= low:
            product.tier = "entry"
        elif price <= high:
            product.tier = "mid"
        else:
            product.tier = "high"

    return products


def get_recommendations(products: list[ScoredProduct], top_n: int = 5) -> list[ScoredProduct]:
    """Get top N recommendations by score."""
    sorted_products = sorted(products, key=lambda p: p.overall_score, reverse=True)
    recommendations = sorted_products[:top_n]
    for i, product in enumerate(recommendations):
        product.recommendation_rank = i + 1
    return recommendations


def export_to_csv(products: list[ScoredProduct]) -> bytes:
    """Export products to CSV bytes."""
    data = [
        {
            "title": p.product.title,
            "price": p.product.price,
            "marketplace": p.product.marketplace,
            "url": p.product.url,
            "overall_score": p.overall_score,
            "tier": p.tier,
            "rank": p.recommendation_rank,
            **{f"score_{k}": v for k, v in p.criteria_scores.items()},
        }
        for p in products
    ]
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue()
```

### Integration Points
```yaml
DEPENDENCIES:
  - modify: pyproject.toml
  - add: "pandas>=2.0.0"
  - add: "playwright>=1.40.0"
  - run: uv sync
  - run: playwright install chromium

CONFIG:
  - modify: src/core/config.py
  - add: scraping_delay_seconds, max_products_per_url, scraping_timeout_ms, headless_browser

API ROUTES:
  - modify: src/api/routes.py
  - add: POST /api/gems (main endpoint)
  - add: GET /api/gems/csv (CSV download)

FRONTEND:
  - create: src/static/gem_finder.html
  - create: src/static/gem_finder.js
```

## Validation Loop

### Level 1: Syntax & Style
```bash
cd /Users/danielmedina/Documents/claude_projects/context-engineering-intro/photo-marketplace-search

uv sync
playwright install chromium
uv run ruff format .
uv run ruff check --fix .
uv run mypy src/

# Expected: No errors
```

### Level 2: Unit Tests
```python
# Tests in src/tests/test_gem_finder.py

import pytest
from src.models.gem_finder import ScrapedProduct, CriteriaSet, EvaluationCriterion
from src.services.scraper import detect_marketplace, normalize_price
from src.services.analysis_service import assign_tiers, score_products

class TestScraper:
    def test_detect_marketplace_vinted(self):
        assert detect_marketplace("https://www.vinted.fr/catalog?q=book") == "vinted"

    def test_detect_marketplace_leboncoin(self):
        assert detect_marketplace("https://www.leboncoin.fr/recherche?text=livre") == "leboncoin"

    def test_detect_marketplace_unknown(self):
        assert detect_marketplace("https://example.com") == "unknown"

    def test_normalize_price_french(self):
        assert normalize_price("49,99 €") == 49.99

    def test_normalize_price_none(self):
        assert normalize_price(None) is None

    def test_normalize_price_invalid(self):
        assert normalize_price("not a price") is None


class TestModels:
    def test_scraped_product(self):
        product = ScrapedProduct(
            marketplace="vinted",
            title="Test Book",
            price=10.99,
            url="https://vinted.fr/item/123",
        )
        assert product.marketplace == "vinted"
        assert product.price == 10.99


class TestAnalysis:
    def test_assign_tiers_empty(self):
        result = assign_tiers([])
        assert result == []
```

```bash
uv run pytest src/tests/test_gem_finder.py -v
```

### Level 3: Integration Test
```bash
# Start the service
uv run uvicorn src.main:app --reload --port 8000

# Test gem finder endpoint
curl -X POST http://localhost:8000/api/gems \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.vinted.fr/catalog?search_text=livre"]}'

# Expected: JSON with recommendations
```

## Final Validation Checklist
- [ ] Dependencies installed: `uv sync && playwright install chromium`
- [ ] All tests pass: `uv run pytest src/tests/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Can import links from Feature 1 response
- [ ] Can add/remove URLs in UI
- [ ] Scraping works (at least Vinted)
- [ ] Claude generates criteria (or fallback used)
- [ ] Products ranked and tiered correctly
- [ ] CSV download works with UTF-8 encoding
- [ ] Progress indicators shown during scraping
- [ ] Graceful error handling for failed URLs

---

## Anti-Patterns to Avoid
- ❌ Don't crash on scraping failures - always return empty list
- ❌ Don't skip rate limiting - add delays between requests
- ❌ Don't ignore encoding - use UTF-8 with BOM for CSV
- ❌ Don't over-engineer - ONE scraper file, not five
- ❌ Don't block UI during scraping - use progress indicators

---

## Comparison: Old vs New Approach

| Aspect | Old (httpx + vinted-scraper) | New (Playwright) |
|--------|------------------------------|------------------|
| **Files** | 5 (base, vinted, leboncoin, abebooks, factory) | 1 (scraper.py) |
| **Lines** | ~300 | ~80 |
| **Dependencies** | vinted-scraper, httpx, beautifulsoup4 | playwright |
| **Leboncoin** | Won't work (DataDome blocks httpx) | May work (real browser) |
| **Vinted** | Depends on vinted-scraper package | Works (real browser) |
| **Complexity** | High (abstract classes, factory pattern) | Low (one async function) |
| **Maintenance** | Update each scraper separately | Update selectors in one dict |

---

## Confidence Score: 7.5/10

**Rationale:**
- (+) Much simpler architecture - one file instead of five
- (+) Real browser = better chance against anti-bot
- (+) Unified approach for all marketplaces
- (+) Easy to add new marketplaces (just add selectors)
- (+) Less external dependencies
- (-) Playwright is heavier than httpx (needs browser)
- (-) CSS selectors may need updates if sites change
- (-) Leboncoin may still block with CAPTCHA
- (-) Slower than direct API calls

**Risk Mitigation:**
- Graceful degradation throughout
- Default criteria if Claude fails
- Empty list returns instead of errors
- User-visible error reporting
- Selector fallback chains

---

## Future Enhancements (Out of Scope)
1. Add more marketplaces by extending SELECTORS dict
2. Use Claude to score products (not just generate criteria)
3. Add price history tracking
4. Implement browser session persistence for anti-bot

---

## Implementation Learnings (December 2024)

### Status: REVERTED
The Gem Finder feature was fully implemented and tested but reverted due to persistent anti-bot blocking on Leboncoin. The Photo Search feature remains the core product.

### Issues Encountered & Fixed

#### 1. Back Link Navigation
**Problem**: "Back to Photo Search" link went to `/` which showed JSON API response instead of UI.
**Fix**: Changed `href="/"` to `href="index.html"` in gem_finder.html.

#### 2. Vinted Selector Issues
**Problem**: Product titles were showing prices (e.g., "15,00 €") instead of actual titles.
**Root Cause**: Generic CSS selectors (`h3`) were matching price elements.
**Fix**: Updated selectors to use more specific `data-testid` attributes:
```python
"vinted": {
    "container": "[data-testid='grid-item'], .feed-grid__item",
    "title": "[data-testid='description-title'], .web_ui__Text__title",
    "price": "[data-testid='price-text'], .web_ui__Text__subtitle",
    ...
}
```

#### 3. Leboncoin Anti-Bot Protection (DataDome)
**Problem**: Leboncoin uses DataDome anti-bot service which blocked all scraping attempts.
**Symptoms**:
- Page loads but shows 0 products scraped
- Cookie consent clicked successfully (progress!)
- Correct page title visible ("smeg Toute la France - leboncoin")
- Product container selectors return empty results

**DataDome Detection Methods**:
- TLS fingerprinting
- CDP (Chrome DevTools Protocol) detection
- JavaScript fingerprinting
- WebGL/Canvas fingerprinting
- WebRTC leak detection

### What Worked
- **Vinted scraping**: Successful after selector fixes
- **Cookie consent automation**: Worked for both Vinted and Leboncoin
- **Page navigation**: Pages loaded correctly
- **Claude criteria generation**: Worked as expected with fallback defaults

### Recommended Approach for Future Implementation

#### Use Patchright Instead of Playwright
[Patchright](https://github.com/AzenoIT/patchright) is a drop-in replacement for Playwright that patches the `Runtime.enable` leak, which is a common detection vector.

```python
# Replace this:
from playwright.async_api import async_playwright

# With this:
from patchright.async_api import async_playwright

# Installation:
# uv add patchright
# patchright install chromium
```

**Benefits**:
- Same API as Playwright (easy migration)
- Patches Runtime.enable CDP detection
- Works on Windows, macOS, Linux
- No additional configuration needed

#### Consider Botright for Full Stealth
[Botright](https://github.com/AzenoIT/botright) is built on Patchright with additional anti-detection features:

```python
import botright

async def scrape_with_botright():
    botright_client = await botright.Botright()
    browser = await botright_client.new_browser()
    page = await browser.new_page()
    await page.goto("https://www.leboncoin.fr/...")
```

**Additional Features**:
- Full fingerprint masking
- hCaptcha and reCaptcha solving
- Cloudflare bypass
- More aggressive anti-detection measures

#### Alternative: Next.js JSON Extraction
Leboncoin uses Next.js, which embeds data in `__NEXT_DATA__` script tags. This approach avoids DOM scraping:

```python
async def extract_nextjs_data(page) -> dict | None:
    try:
        script = await page.query_selector("script#__NEXT_DATA__")
        if script:
            content = await script.inner_text()
            return json.loads(content)
    except Exception:
        return None
```

### Why Feature Was Reverted
1. **Leboncoin still blocked**: Even with Patchright, DataDome detection persisted
2. **Limited practical value**: Vinted worked but provided incomplete product data (model, condition, etc.)
3. **Maintenance burden**: CSS selectors change frequently, requiring ongoing updates
4. **User feedback**: "It's not working, and at the end doesn't look very useful"

### Key Takeaways for Future Attempts
1. **Start with Patchright** from the beginning, not regular Playwright
2. **Test Leboncoin manually first** in incognito mode to understand current blocking
3. **Consider API-first approach** if official APIs exist
4. **Build for graceful degradation** - feature should work even if some marketplaces fail
5. **Evaluate ROI early** - anti-bot bypass is an ongoing battle

### Dependencies Removed
```diff
- "patchright>=1.50.0"  # Replaced with regular Playwright later
- "pandas>=2.0.0"       # Only needed for CSV export
```

### Files That Existed (Now Deleted)
```
src/services/scraper.py          # Patchright-based marketplace scraper
src/services/criteria_service.py # Claude-based criteria generation
src/services/analysis_service.py # Product scoring and ranking
src/models/gem_finder.py         # Pydantic models
src/static/gem_finder.html       # Frontend UI
src/static/gem_finder.js         # Frontend JavaScript
src/tests/test_gem_finder.py     # 29 tests for Gem Finder
```

---

**Last Updated**: December 27, 2024
