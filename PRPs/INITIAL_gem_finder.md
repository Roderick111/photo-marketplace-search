## FEATURE:

Build a "Gem Finder" feature that analyzes marketplace listings to find the best quality-to-price items. The workflow:

1. **Link Management**:
   - Import marketplace search links from Feature 1 (object searcher)
   - Allow user to edit the link list (add new links, delete unwanted ones)
   - Support multiple marketplace URLs (Vinted, Leboncoin, Abebooks)

2. **Product Scraping & Data Collection**:
   - Parse all products from the provided marketplace links
   - Extract key data: title, price, description, seller info, location, images, etc.
   - Store data in structured format (CSV/pandas DataFrame)
   - Handle rate limiting and marketplace-specific challenges

3. **Dynamic Criteria Generation** (Claude AI):
   - Analyze the product type/category automatically
   - Define 1-3 relevant evaluation criteria based on product type:
     - Books → Author relevance, edition quality, condition
     - Electronics/Kitchen tools → Brand reputation, model quality, features
     - Clothing → Brand, condition, style relevance
     - General items → Condition, seller rating, age
   - Use Claude to intelligently determine what matters most for each category

4. **Data Analysis & Ranking**:
   - Apply the dynamic criteria to all scraped products
   - Calculate quality-to-price scores
   - Rank products accordingly

5. **Tiered Recommendations** (when relevant):
   - For products with wide price ranges (e.g., kitchen appliances):
     - Entry tier: Best budget options (top 1-2)
     - Mid tier: Best value for money (top 1-2)
     - High tier: Premium quality options (top 1-2)
   - For uniform products (e.g., books): Just top 3-5 overall

6. **Output**:
   - Display top 3-5 recommendations with:
     - Product title and link
     - Price
     - Quality score/reasoning
     - Which criteria it excels in
   - Provide complete CSV file download with all products and scores

**Tech Stack Preferences**:
- Python 3.10+
- Beautiful Soup or Playwright for web scraping (Playwright for dynamic content)
- Pandas for data manipulation and CSV generation
- Claude API for dynamic criteria generation and analysis
- Pydantic for structured outputs
- FastAPI or Streamlit for UI (extend from Feature 1)

**Key Requirements**:
- Fast scraping (parallel requests when possible)
- Respectful rate limiting (don't overload marketplaces)
- Robust error handling (some links may be broken or products removed)
- Clear progress indicators (scraping 50+ products takes time)
- CSV export with all columns: title, price, URL, scores, criteria values
- Clean presentation of top recommendations

## EXAMPLES:

### 1. Vinted Scraper with Structured Data
**Source**: [GitHub - Giglium/vinted_scraper](https://github.com/Giglium/vinted_scraper)

Simple Python package for scraping Vinted:
```python
import vinted_scraper.VintedScraper

scraper = VintedScraper("https://www.vinted.com")
params = {"search_text": "board games"}
items = scraper.search(params)
# Returns VintedItem objects with structured data
```

**Key patterns**:
- Uses Vinted's API under the hood (more reliable than HTML parsing)
- Returns structured `VintedItem` objects
- Simple search interface with parameters
- Also available on PyPI: `vinted-scraper`

**Useful for**: Understanding how to efficiently scrape Vinted listings with minimal code

### 2. Leboncoin BeautifulSoup Scraper
**Source**: [GitHub - AyedSamy/LeBonCoin-Web-Scraper](https://github.com/AyedSamy/LeBonCoin-Web-Scraper)

Extracts comprehensive product data:
- Product name (`p[data-qa-id=aditem_title]`)
- Price (`span._1C-CB`)
- Category, seller type, location
- Publication date, shipping info
- Product image URLs

**Key patterns**:
- CSS selectors for precise data extraction
- Try-except blocks for optional fields (defaults to 'none')
- Handles missing data gracefully

**Useful for**: Learning Leboncoin's HTML structure and what data is available

### 3. Claude Analysis Tool for CSV Data
**Source**: [Claude Analysis Tool](https://claude.com/blog/analysis-tool)

Claude can process CSV data with JavaScript code execution:
- Upload CSV files directly
- Analyze data systematically
- Generate mathematically precise insights
- Create dashboards and visualizations

**Key patterns**:
- Step-by-step data processing
- Reproducible, precise results
- Can handle marketing funnels, sales data, engagement metrics

**Useful for**: Understanding Claude's native CSV analysis capabilities

### 4. Pandas DataFrame to CSV Export
**Source**: [Pandas DataFrame.to_csv Documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)

Simple CSV generation:
```python
import pandas as pd

# Create DataFrame with product data
df = pd.DataFrame({
    'title': [...],
    'price': [...],
    'quality_score': [...],
    'url': [...]
})

# Export to CSV
df.to_csv('products_analysis.csv', index=False, encoding='utf-8')
```

**Key patterns**:
- `index=False` to exclude row numbers
- `encoding='utf-8'` for special characters
- Can specify delimiter, quote characters, etc.

**Useful for**: Quick CSV export for user download

### 5. Product Price Analysis with Pandas
**Source**: [E-commerce Price Monitoring Analysis Using Python](https://medium.com/@samueloyedele/ecommerce-price-monitoring-analysis-using-python-laptop-7ddca1fa8fdf)

Shows how to analyze product prices by brand:
```python
# Group by brand and calculate average prices
df.groupby('brand')['price'].mean()

# Find best value (high rating, low price)
df['value_score'] = df['rating'] / df['price']
top_value = df.nlargest(5, 'value_score')
```

**Useful for**: Understanding quality-to-price scoring patterns

## DOCUMENTATION:

### Claude API
- **Structured Outputs**: [Claude Structured Outputs](https://claude.com/blog/structured-outputs-on-the-claude-developer-platform)
  - Ensures API responses match JSON schemas
  - Available for Claude Sonnet 4.5 and Opus 4.1
  - Use `output_format` parameter for guaranteed schema compliance

- **Claude Data Analysis**: [Using Claude for Data Analytics](https://blog.coupler.io/how-to-use-claude-ai-for-data-analytics/)
  - Upload CSV files directly to Claude
  - Clear headers, standard date formats recommended
  - Claude can generate criteria dynamically based on data patterns

### Web Scraping

- **Vinted Scraper Package**: [vinted-scraper on PyPI](https://pypi.org/project/vinted-scraper/)
  - Install: `pip install vinted-scraper`
  - API-based scraping (more stable than HTML parsing)

- **Leboncoin Scraping Guide**: [How to Scrape Leboncoin with Python](https://scrapfly.io/blog/posts/how-to-scrape-leboncoin-marketplace-real-estate)
  - Notes: Leboncoin has scraper detection
  - Recommends Playwright for browser automation
  - Need to handle anti-bot measures

- **BeautifulSoup Docs**: [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
  - CSS selector reference
  - HTML parsing techniques

- **Playwright Python**: [Playwright for Python](https://playwright.dev/python/)
  - For dynamic content and JavaScript-heavy sites
  - Browser automation with anti-detection

### Pandas & CSV

- **Pandas CSV Reference**: [pandas.DataFrame.to_csv](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)
  - Complete CSV export options
  - Encoding, delimiters, headers

- **Pandas Data Analysis**: [Pandas Analyzing DataFrames](https://www.w3schools.com/python/pandas/pandas_analyzing.asp)
  - Basic statistics, grouping, sorting
  - Data cleaning and transformation

### Dynamic Pricing/Criteria (ML Concepts)

- **Multi-Criteria Decision Making**: [Multi-Criteria Decision Making in Python](https://sustainabilitymethods.org/index.php/Multi-Criteria_Decision_Making_in_Python)
  - NumPy/Pandas for decision matrices
  - Different criteria weights

- **Dynamic Pricing ML Study**: [Dynamic Pricing Method in E-Commerce Using ML](https://www.mdpi.com/2076-3417/14/24/11668)
  - Criteria determination for ML models
  - SVM, Decision Trees, k-NN approaches

## OTHER CONSIDERATIONS:

### Common Gotchas

1. **Marketplace Scraping Challenges**:
   - **Rate limiting**: Leboncoin and Vinted have anti-scraping measures
   - **IP blocking**: Use polite delays (2-5 seconds between requests)
   - **Dynamic content**: Some marketplaces use JavaScript rendering
   - **Session cookies**: May need to maintain session state
   - **Robots.txt**: Check and respect marketplace policies
   - **Legal considerations**: Scraping for personal use vs commercial

2. **Data Quality Issues**:
   - Missing prices (some listings are "offers" or negotiable)
   - Inconsistent formats (€50, 50€, 50 euros, etc.)
   - Duplicate listings (same seller posting multiple times)
   - Outdated listings (product already sold)
   - Misleading titles (seller keywords stuffing)
   - Images may be missing or broken links

3. **Claude Dynamic Criteria Generation**:
   - **Prompt engineering critical**: Must be very specific about:
     - What product category we're analyzing
     - What data fields are available
     - Expected output format (JSON with criteria names + weights)
   - **Example prompt structure**:
     ```
     Analyze these 50 kitchen appliance listings.
     Available data: title, price, brand, seller_rating, condition, year
     Generate 2-3 evaluation criteria that matter most for kitchen appliances.
     Return as JSON: {criteria: [{name, weight, reasoning}]}
     ```
   - **Fallback criteria**: Have defaults if Claude can't determine category

4. **Performance Considerations**:
   - **Parallel scraping**: Use `asyncio` or `concurrent.futures` for multiple URLs
   - **Caching**: Don't re-scrape same URLs within same session
   - **Progress tracking**: Show user "Scraped 15/50 products..."
   - **Timeout handling**: Some pages may hang, set max timeout (10s)
   - **Memory**: For 100+ products, consider streaming to CSV

5. **Price Normalization**:
   - Clean price strings: "50 €" → 50.0
   - Handle decimals: "49,99" vs "49.99"
   - Currency conversion if needed (though all should be EUR)
   - Watch for outliers (price = 0, or 999999)

6. **Quality Score Calculation**:
   - Different criteria need different normalization:
     - **Price**: Lower is better (inverse scale)
     - **Condition**: "New" > "Excellent" > "Good" > "Fair"
     - **Seller rating**: Higher is better (direct scale)
     - **Brand reputation**: May need manual mapping or Claude rating
   - **Combined score formula**: Weighted average or multiplicative
   - **Edge cases**: What if product excels in one criteria but fails others?

7. **Tiered Recommendations Logic**:
   - Define price buckets dynamically:
     ```python
     price_low = df['price'].quantile(0.33)  # Bottom 33%
     price_high = df['price'].quantile(0.66) # Top 33%

     entry = df[df['price'] <= price_low]
     mid = df[(df['price'] > price_low) & (df['price'] <= price_high)]
     high = df[df['price'] > price_high]
     ```
   - Within each tier, sort by quality score
   - Some categories don't need tiers (e.g., books usually narrow price range)

8. **CSV Export Details**:
   - Include all raw data + computed columns
   - Columns to include:
     - `title`, `price`, `url`, `marketplace`, `seller`, `location`
     - `criteria_1_score`, `criteria_2_score`, `criteria_3_score`
     - `overall_quality_score`, `tier` (entry/mid/high/none)
     - `recommendation_rank` (1-5 for top picks, null for others)
   - UTF-8 encoding for French accents
   - Excel-compatible format (comma delimiter, quoted strings)

9. **Error Handling Strategy**:
   - **Network errors**: Retry 3 times with exponential backoff
   - **Parse errors**: Log the URL, continue with other products
   - **Missing required fields**: Skip product or use placeholder
   - **Claude API failures**: Fallback to predefined criteria
   - **User feedback**: Show which URLs failed to scrape

10. **UI/UX Considerations**:
    - **Link input**: Textarea with one URL per line, or file upload
    - **Progress bar**: Real-time scraping progress
    - **Preview mode**: Show first 10 products before full analysis
    - **Filter options**: Let user filter by marketplace, price range
    - **Sort options**: By price, by score, by marketplace
    - **Mobile responsive**: CSV download should work on mobile

11. **Dependencies**:
    - `anthropic` - Claude API client
    - `beautifulsoup4` - HTML parsing
    - `playwright` - Browser automation (for dynamic sites)
    - `pandas` - Data manipulation
    - `requests` or `httpx` - HTTP requests
    - `pydantic` - Data validation
    - `python-dotenv` - Environment variables
    - `vinted-scraper` - Optional, if using Vinted API approach

12. **Abebooks Scraping**:
    - **Note**: No ready-made scraper found in research
    - May need to build custom scraper
    - Check Abebooks robots.txt and terms of service
    - Consider using their affiliate API if available (more reliable)
    - HTML structure likely different from Vinted/Leboncoin

13. **Context7 MCP Usage**:
    - Use Context7 to get latest documentation for scraping libraries
    - Helpful for: BeautifulSoup selectors, Playwright API, Pandas methods
    - Example: "use context7 for playwright python latest selectors"

14. **Serena MCP Usage**:
    - Use Serena for semantic code analysis when building scrapers
    - Helpful for refactoring complex scraping logic
    - Can assist with LSP-powered code navigation

Important: Use Serena and Context7 MCPs for better performance and reliability during development.
