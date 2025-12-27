name: "Photo to Marketplace Search - Vision API Integration"
description: |

## Purpose
Build a production-ready web application that converts uploaded photos into marketplace search links using Claude Vision API. The system identifies objects in images and routes users to appropriate French marketplaces (Abebooks.fr for books, Vinted for clothing, Leboncoin for everything else).

## Core Principles
1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **Global rules**: Follow all rules in CLAUDE.md (KISS, YAGNI, UV package management)

---

## Goal
Create a single-page web application where users upload photos and receive clickable marketplace search links within 5 seconds. The app uses Claude Vision API to identify objects and intelligently routes to appropriate marketplaces.

## Why
- **Business value**: Simplifies secondhand marketplace searching for French users
- **User impact**: Eliminates manual product description writing for marketplace searches
- **Integration**: Demonstrates Claude Vision API practical application
- **Problems solved**: Reduces friction in finding similar items across multiple marketplaces

## What
A FastAPI-based web application with:
- Drag-and-drop or button-based image upload interface
- Claude Vision API integration for object detection and categorization
- Smart marketplace routing based on object type
- Generated search URLs for Abebooks.fr, Vinted, and Leboncoin
- Clean, minimal UI with fast response times

### Success Criteria
- [ ] Image upload accepts JPG, PNG, JPEG, WebP formats (max 10MB)
- [ ] Claude Vision API successfully identifies objects and generates 1-3 search queries
- [ ] Objects correctly routed to appropriate marketplaces (books→Abebooks, clothing→Vinted, other→Leboncoin)
- [ ] Returns 3-5 clickable marketplace search URLs
- [ ] Total processing time < 5 seconds from upload to results
- [ ] Proper error handling for unidentifiable images or API failures
- [ ] All tests pass and code meets CLAUDE.md quality standards

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window

# Claude Vision API
- url: https://docs.claude.com/en/docs/build-with-claude/vision
  why: Official documentation for image input methods (base64, Files API, URL)
  critical: Use claude-sonnet-4-20250514 model, supports PNG/JPEG/WebP/GIF, 10MB limit

- url: https://collabnix.com/claude-api-integration-guide-2025-complete-developer-tutorial-with-code-examples/
  why: 2025 Python examples for base64 image encoding with Claude
  critical: Shows proper message structure with image and text content types

# FastAPI File Upload
- url: https://fastapi.tiangolo.com/tutorial/request-files/
  why: Official FastAPI file upload documentation
  critical: Use UploadFile for efficient handling, requires python-multipart

- url: https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/
  why: Complete guide to secure file handling in FastAPI
  critical: File validation, size limits, async operations, security considerations

- url: https://fastapi.tiangolo.com/reference/uploadfile/
  why: UploadFile class reference
  critical: Async methods (read(), seek(), close())

# Pydantic for Structured Outputs
- url: https://pydantic.dev/articles/llm-vision
  why: Building product search with Vision API and Pydantic
  critical: Use model_json_schema() to embed validation rules in prompts

- url: https://docs.pydantic.dev/
  why: Pydantic v2 documentation for data validation
  critical: Project uses Pydantic v2, structured output validation patterns

# Project Standards
- file: CLAUDE.md
  why: Project coding standards, UV usage, testing patterns, structure limits
  critical:
    - Use UV for package management (never update pyproject.toml directly)
    - Max 500 lines per file, 50 lines per function, 100 lines per class
    - Use venv_linux for all Python commands
    - Vertical slice architecture with tests next to code
    - Google-style docstrings required
    - Line length max 100 characters

# Marketplace URL Patterns (from initial.md)
- pattern: Abebooks.fr books search
  url: https://www.abebooks.fr/servlet/SearchResults?kn={query}&sts=t
  encoding: Use urllib.parse.quote() for query parameter

- pattern: Vinted clothing search
  url: https://www.vinted.fr/catalog?search_text={query}
  encoding: Use urllib.parse.quote() for query parameter

- pattern: Leboncoin general search
  url: https://www.leboncoin.fr/recherche?text={query}
  encoding: Use urllib.parse.quote() for query parameter
```

### Current Codebase Tree
```bash
.
├── CLAUDE.md                    # Project coding standards
├── README.md
├── PRPs/
│   ├── templates/
│   │   └── prp_base.md
│   └── photo-to-marketplace-search.md  # This PRP
├── use-cases/
│   ├── pydantic-ai/
│   │   └── examples/
│   │       └── structured_output_agent/
│   │           └── agent.py    # Reference for Pydantic patterns
│   └── agent-factory-with-subagents/
│       └── examples/
│           └── main_agent_reference/
│               └── settings.py  # Reference for env config patterns
├── .gitignore
└── .gitattributes

# NOTE: No existing Python web apps in codebase - this is a greenfield project
# NOTE: No pyproject.toml exists yet - will be created following UV standards
```

### Desired Codebase Tree with Files to be Added
```bash
photo-marketplace-search/
├── pyproject.toml               # UV-managed dependencies
├── .env.example                 # Environment variables template
├── .env                         # Local environment (gitignored)
├── .gitignore                   # Ignore .env, __pycache__, .venv, etc.
├── README.md                    # Setup and usage instructions
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # Upload endpoint, health check
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vision_service.py    # Claude Vision API integration
│   │   └── url_builder.py       # Marketplace URL construction
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py          # Request Pydantic models
│   │   └── responses.py         # Response Pydantic models
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings with pydantic-settings
│   │   └── exceptions.py        # Custom exceptions
│   │
│   ├── static/
│   │   ├── index.html           # Upload interface
│   │   ├── styles.css           # Minimal styling
│   │   └── script.js            # Upload handling, results display
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py          # Pytest fixtures
│       ├── test_vision_service.py
│       ├── test_url_builder.py
│       ├── test_routes.py
│       └── test_integration.py  # End-to-end tests
│
└── uploads/                     # Temporary upload directory (gitignored)
    └── .gitkeep
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Claude Vision API (2025)
# - Model: Use claude-sonnet-4-20250514 for best vision performance
# - Max image size: 10MB per image
# - Supported formats: PNG, JPEG, WebP, GIF (non-animated)
# - Beta header: For Files API use anthropic-beta: files-api-2025-04-14
# - Base64 encoding: Must decode bytes to string after base64.b64encode()
# - Media type: Must match file extension (image/jpeg, image/png, image/webp)

# CRITICAL: FastAPI File Upload
# - Install python-multipart: Required for form data support
# - Use UploadFile type: Efficient for large files, spools to disk after 1MB
# - Async methods: await file.read(), file methods run in threadpool
# - File validation: Check content type AND magic numbers for security
# - Size limits: Validate before processing, default FastAPI limit is 1MB
# - Cleanup: Always close files and delete temporary uploads after processing

# CRITICAL: Pydantic v2 (from CLAUDE.md)
# - Use Field(...) for required fields with validation
# - Use model_json_schema() to generate JSON schema for prompts
# - Structured outputs: Pass schema to Claude for better JSON compliance
# - Validation: Pydantic automatically validates responses from Claude

# CRITICAL: UV Package Management (from CLAUDE.md)
# - NEVER update pyproject.toml directly
# - ALWAYS use: uv add <package> or uv add --dev <package>
# - Install packages: uv sync
# - Run commands: uv run <command>

# CRITICAL: URL Encoding
# - Use urllib.parse.quote() for search queries
# - Test generated URLs in browser before deploying
# - Handle special characters: spaces, accents, symbols
# - Some marketplaces may have rate limiting

# CRITICAL: Error Handling
# - Claude API can fail (rate limits, network issues)
# - Image may be too blurry or unclear for identification
# - Provide user-friendly error messages
# - Log errors for debugging but don't expose API details

# CRITICAL: Response Time Target
# - Vision API calls typically take 2-5 seconds
# - Add loading indicator in UI
# - Consider caching: Same image hash → cached results
# - Set timeout on API calls (30 seconds max)

# CRITICAL: Security (from FastAPI best practices)
# - Validate file types: Check magic numbers, not just extensions
# - Set max file size: 10MB to match Claude API limit
# - Don't trust filenames: Generate UUIDs for temporary storage
# - Clean up uploads: Delete files after processing to prevent disk fill
# - Rate limiting: Prevent API key abuse
# - CORS: Configure appropriately for production

# CRITICAL: Testing with venv_linux (from CLAUDE.md)
# - Always use venv_linux for running pytest
# - Pattern: uv run pytest tests/ -v
```

## Implementation Blueprint

### Data Models and Structure

Create the core data models to ensure type safety and consistency.

```python
# src/models/requests.py
from pydantic import BaseModel, Field, validator
from typing import Literal

class ImageUploadResponse(BaseModel):
    """Response from image upload validation."""
    filename: str
    size: int
    content_type: str

# src/models/responses.py
from pydantic import BaseModel, Field
from typing import List, Literal

class SearchQuery(BaseModel):
    """Individual search query generated from image."""
    query: str = Field(..., min_length=1, max_length=200)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)

class MarketplaceLink(BaseModel):
    """Marketplace search link with metadata."""
    marketplace: Literal["abebooks", "vinted", "leboncoin"]
    query: str
    url: str

class VisionAnalysisResult(BaseModel):
    """Structured output from Claude Vision API."""
    object_type: Literal["book", "clothing", "electronics", "furniture", "tools", "general"]
    description: str = Field(..., min_length=1)
    search_queries: List[SearchQuery] = Field(..., min_items=1, max_items=3)
    confidence: float = Field(ge=0.0, le=1.0)

class MarketplaceSearchResponse(BaseModel):
    """Final response with marketplace links."""
    analysis: VisionAnalysisResult
    marketplace_links: List[MarketplaceLink] = Field(..., min_items=1, max_items=5)
    processing_time_seconds: float

# src/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Configuration
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    claude_model: str = Field(default="claude-sonnet-4-20250514")

    # File Upload Configuration
    max_upload_size_mb: int = Field(default=10)
    allowed_extensions: set = Field(default={".jpg", ".jpeg", ".png", ".webp"})
    upload_dir: str = Field(default="uploads")

    # API Limits
    vision_api_timeout: int = Field(default=30)
    max_concurrent_uploads: int = Field(default=10)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# src/core/exceptions.py
class VisionAPIError(Exception):
    """Raised when Claude Vision API fails."""
    pass

class ImageValidationError(Exception):
    """Raised when uploaded image fails validation."""
    pass

class MarketplaceRoutingError(Exception):
    """Raised when marketplace routing fails."""
    pass
```

### List of Tasks to be Completed (in order)

```yaml
Task 1: Initialize Project Structure with UV
CREATE pyproject.toml:
  - Use: uv init
  - Add dependencies: uv add fastapi uvicorn anthropic pydantic pydantic-settings python-multipart aiofiles pillow python-dotenv
  - Add dev dependencies: uv add --dev pytest pytest-asyncio pytest-cov httpx ruff mypy
  - VERIFY: pyproject.toml follows UV standards
  - VERIFY: Line length set to 100 in ruff config

CREATE .env.example:
  - Include all required environment variables with descriptions
  - Pattern: ANTHROPIC_API_KEY=your_api_key_here
  - Pattern: CLAUDE_MODEL=claude-sonnet-4-20250514

CREATE .gitignore:
  - Ignore: .env, __pycache__/, .venv/, uploads/, .pytest_cache/, .mypy_cache/

Task 2: Implement Core Configuration
CREATE src/core/config.py:
  - PATTERN: Use pydantic-settings with dotenv
  - PATTERN: Follow examples/main_agent_reference/settings.py structure
  - Load environment variables with load_dotenv()
  - Validate required API key is present
  - Provide sensible defaults for timeouts and limits

CREATE src/core/exceptions.py:
  - Define custom exceptions: VisionAPIError, ImageValidationError, MarketplaceRoutingError
  - Include descriptive error messages
  - PATTERN: Inherit from Exception, add custom __init__ if needed

Task 3: Implement Data Models
CREATE src/models/requests.py:
  - ImageUploadResponse model with validation
  - PATTERN: Use Pydantic v2 Field() with constraints

CREATE src/models/responses.py:
  - VisionAnalysisResult with Literal types for categories
  - SearchQuery with confidence scores
  - MarketplaceLink with enum for marketplace names
  - MarketplaceSearchResponse with timing metadata
  - PATTERN: Use Field() with min/max constraints
  - PATTERN: Use Literal for fixed choices (book, clothing, etc.)

Task 4: Implement Vision Service
CREATE src/services/vision_service.py:
  - PATTERN: Async functions for API calls
  - PATTERN: Follow Claude Vision API base64 example from collabnix.com
  - Read image file and convert to base64
  - Determine media type from file extension
  - Build Claude API message with image and text content
  - Include VisionAnalysisResult JSON schema in system prompt
  - Parse and validate response with Pydantic
  - Handle API errors gracefully with retries
  - Set timeout to vision_api_timeout from config
  - GOTCHA: Base64 encode then decode to string
  - GOTCHA: Media type must match file format exactly

Task 5: Implement URL Builder Service
CREATE src/services/url_builder.py:
  - PATTERN: Pure functions for URL construction
  - Map object_type to marketplace (book→abebooks, clothing→vinted, other→leboncoin)
  - Build URLs using marketplace patterns from initial.md
  - Use urllib.parse.quote() for query encoding
  - Generate 3-5 links from search queries
  - GOTCHA: URL-encode special characters properly
  - VERIFY: Test generated URLs manually in browser

Task 6: Implement API Routes
CREATE src/api/routes.py:
  - PATTERN: Async FastAPI endpoint with UploadFile
  - PATTERN: Follow FastAPI file upload documentation
  - POST /api/analyze endpoint
  - Validate file size (max 10MB)
  - Validate file type (magic numbers + extension)
  - Save to temporary location with UUID filename
  - Call vision_service.analyze_image()
  - Call url_builder.build_marketplace_links()
  - Delete temporary file after processing
  - Return MarketplaceSearchResponse
  - GET /health endpoint for health checks
  - GOTCHA: Use await file.read() for async operations
  - GOTCHA: Always cleanup temporary files in finally block

Task 7: Implement Main FastAPI App
CREATE src/main.py:
  - Initialize FastAPI app with metadata
  - Include CORS middleware for development
  - Mount static files directory
  - Include API routes
  - Add exception handlers for custom exceptions
  - Add startup/shutdown events for resource management
  - PATTERN: Use get_settings() for dependency injection
  - PATTERN: Follow FastAPI best practices from documentation

Task 8: Create Frontend Interface
CREATE src/static/index.html:
  - Simple single-page layout
  - Drag-and-drop file upload area
  - Button-based upload fallback
  - Loading indicator during processing
  - Results display area for marketplace links
  - Error message display area
  - PATTERN: Minimal, functional design

CREATE src/static/styles.css:
  - Clean, minimal styling
  - Responsive design for mobile/desktop
  - Loading spinner animation
  - Button hover states

CREATE src/static/script.js:
  - Handle file upload via FormData
  - Show loading indicator during API call
  - Display results as clickable links
  - Handle and display errors gracefully
  - PATTERN: Async/await for fetch calls

Task 9: Implement Comprehensive Tests
CREATE src/tests/conftest.py:
  - PATTERN: Pytest fixtures for test dependencies
  - Mock Anthropic API client
  - Test FastAPI client fixture
  - Temporary upload directory fixture

CREATE src/tests/test_vision_service.py:
  - Test image base64 encoding
  - Test media type detection
  - Test API request structure
  - Test response parsing and validation
  - Test error handling (API failures, invalid responses)
  - PATTERN: Use pytest-asyncio for async tests
  - PATTERN: Mock anthropic.Anthropic client

CREATE src/tests/test_url_builder.py:
  - Test marketplace routing logic
  - Test URL encoding
  - Test URL construction for each marketplace
  - Test edge cases (special characters, accents)
  - PATTERN: Use pytest.mark.parametrize for multiple test cases

CREATE src/tests/test_routes.py:
  - Test /api/analyze endpoint with valid image
  - Test file validation (size, type)
  - Test error responses
  - Test /health endpoint
  - PATTERN: Use httpx.AsyncClient for API testing
  - PATTERN: Use TestClient from fastapi.testclient

CREATE src/tests/test_integration.py:
  - End-to-end test: upload image → get marketplace links
  - Test with different object types (book, clothing, electronics)
  - Test error scenarios (blurry image, API failure)
  - PATTERN: Use real test images in tests/fixtures/
  - VERIFY: All tests must pass before marking complete

Task 10: Create Documentation
CREATE README.md:
  - Project description and features
  - Setup instructions (UV installation, dependencies)
  - Environment variable configuration
  - Running the application (uvicorn command)
  - Running tests (pytest command)
  - API documentation (endpoints, request/response formats)
  - Troubleshooting section
  - PATTERN: Follow examples/README.md structure from codebase
```

### Per Task Pseudocode (Critical Tasks Only)

```python
# Task 4: Vision Service Implementation
async def analyze_image(image_path: str, settings: Settings) -> VisionAnalysisResult:
    """
    Analyze image using Claude Vision API and return structured results.

    CRITICAL STEPS:
    1. Read image file and encode to base64
    2. Determine media type from extension
    3. Build Claude API message with embedded JSON schema
    4. Call API with timeout and error handling
    5. Parse and validate response with Pydantic
    """
    # PATTERN: Context manager for file handling
    async with aiofiles.open(image_path, "rb") as f:
        image_bytes = await f.read()

    # GOTCHA: Must decode base64 bytes to string
    image_data = base64.b64encode(image_bytes).decode("utf-8")

    # GOTCHA: Media type must match file format exactly
    media_type = get_media_type(image_path)  # "image/jpeg", "image/png", etc.

    # PATTERN: Use Pydantic model_json_schema() in prompt
    schema = VisionAnalysisResult.model_json_schema()

    # Build system prompt with schema
    system_prompt = f"""
    You are an expert at analyzing product images for marketplace searches.
    Identify the object type (book, clothing, electronics, furniture, tools, or general).
    Generate 1-3 descriptive search queries in French.
    Return your analysis in this JSON format:
    {json.dumps(schema, indent=2)}
    """

    # PATTERN: Anthropic client with message API
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    try:
        # CRITICAL: Use async with timeout
        response = await asyncio.wait_for(
            client.messages.create(
                model=settings.claude_model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": "Analyze this image and provide structured output."
                            }
                        ]
                    }
                ]
            ),
            timeout=settings.vision_api_timeout
        )

        # PATTERN: Extract JSON from response
        response_text = response.content[0].text

        # PATTERN: Parse and validate with Pydantic
        analysis = VisionAnalysisResult.model_validate_json(response_text)
        return analysis

    except asyncio.TimeoutError:
        raise VisionAPIError("Vision API request timed out")
    except anthropic.APIError as e:
        raise VisionAPIError(f"Vision API error: {e}")
    except ValueError as e:
        raise VisionAPIError(f"Invalid response format: {e}")

# Task 5: URL Builder Implementation
def build_marketplace_links(
    analysis: VisionAnalysisResult,
) -> List[MarketplaceLink]:
    """
    Build marketplace search URLs based on object type and queries.

    CRITICAL STEPS:
    1. Map object_type to marketplace
    2. For each search query, build appropriate URL
    3. URL-encode query parameters
    4. Return list of MarketplaceLink objects
    """
    # PATTERN: Marketplace routing logic
    marketplace_map = {
        "book": ("abebooks", "https://www.abebooks.fr/servlet/SearchResults?kn={}&sts=t"),
        "clothing": ("vinted", "https://www.vinted.fr/catalog?search_text={}"),
        # Default to leboncoin for all others
    }

    marketplace_name, url_template = marketplace_map.get(
        analysis.object_type,
        ("leboncoin", "https://www.leboncoin.fr/recherche?text={}")
    )

    links = []
    for search_query in analysis.search_queries[:5]:  # Max 5 links
        # CRITICAL: URL-encode the query
        encoded_query = urllib.parse.quote(search_query.query)

        # Build full URL
        url = url_template.format(encoded_query)

        links.append(MarketplaceLink(
            marketplace=marketplace_name,
            query=search_query.query,
            url=url
        ))

    return links

# Task 6: API Routes Implementation
@router.post("/api/analyze", response_model=MarketplaceSearchResponse)
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """
    Analyze uploaded image and return marketplace search links.

    CRITICAL STEPS:
    1. Validate file size and type
    2. Save to temporary location
    3. Call vision service
    4. Build marketplace URLs
    5. Clean up temporary file
    6. Return results with timing
    """
    start_time = time.time()
    temp_path = None

    try:
        # PATTERN: Validate file size (in bytes)
        max_size = settings.max_upload_size_mb * 1024 * 1024
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to start

        if file_size > max_size:
            raise ImageValidationError(f"File too large: {file_size} bytes")

        # PATTERN: Validate file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.allowed_extensions:
            raise ImageValidationError(f"Invalid file type: {ext}")

        # CRITICAL: Validate magic numbers for security
        await validate_image_magic_numbers(file)

        # PATTERN: Save with UUID filename to prevent collisions
        temp_filename = f"{uuid.uuid4()}{ext}"
        temp_path = os.path.join(settings.upload_dir, temp_filename)

        # PATTERN: Async file write
        async with aiofiles.open(temp_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        # Call vision service
        analysis = await vision_service.analyze_image(temp_path, settings)

        # Build marketplace links
        links = url_builder.build_marketplace_links(analysis)

        # Calculate processing time
        processing_time = time.time() - start_time

        return MarketplaceSearchResponse(
            analysis=analysis,
            marketplace_links=links,
            processing_time_seconds=round(processing_time, 2)
        )

    except ImageValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except VisionAPIError as e:
        raise HTTPException(status_code=503, detail="Image analysis failed")
    finally:
        # CRITICAL: Always cleanup temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.error(f"Failed to delete temp file: {e}")
```

### Integration Points

```yaml
ENVIRONMENT:
  - file: .env
  - vars: |
      # Claude API
      ANTHROPIC_API_KEY=sk-ant-...
      CLAUDE_MODEL=claude-sonnet-4-20250514

      # Upload Configuration
      MAX_UPLOAD_SIZE_MB=10
      UPLOAD_DIR=uploads

      # API Limits
      VISION_API_TIMEOUT=30
      MAX_CONCURRENT_UPLOADS=10

DIRECTORIES:
  - create: uploads/
  - gitignore: uploads/*
  - purpose: Temporary storage for uploaded images

STATIC_FILES:
  - mount: /static → src/static/
  - files: index.html, styles.css, script.js
  - serve: FastAPI static file serving

DEPENDENCIES (managed by UV):
  - runtime:
      - fastapi
      - uvicorn[standard]
      - anthropic
      - pydantic
      - pydantic-settings
      - python-multipart
      - aiofiles
      - pillow
      - python-dotenv
  - development:
      - pytest
      - pytest-asyncio
      - pytest-cov
      - httpx
      - ruff
      - mypy
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding

# Format code
uv run ruff format .

# Check linting
uv run ruff check . --fix

# Type checking
uv run mypy src/

# Expected: No errors. If errors, READ the error and fix.
# Common issues:
# - Missing type hints on function parameters/returns
# - Incorrect Pydantic model usage
# - Missing async/await keywords
```

### Level 2: Unit Tests
```python
# src/tests/test_vision_service.py
import pytest
from unittest.mock import Mock, AsyncMock, patch

@pytest.mark.asyncio
async def test_analyze_image_success(tmp_path, mock_anthropic_client):
    """Test successful image analysis with Claude Vision API."""
    # Create test image
    test_image = tmp_path / "test.jpg"
    test_image.write_bytes(b"fake image data")

    # Mock API response
    mock_response = Mock()
    mock_response.content = [Mock(text='{"object_type": "book", "description": "Novel", "search_queries": [{"query": "roman policier", "confidence": 0.9}], "confidence": 0.85}')]
    mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

    # Call service
    result = await analyze_image(str(test_image), settings)

    # Assertions
    assert result.object_type == "book"
    assert len(result.search_queries) == 1
    assert result.search_queries[0].query == "roman policier"

@pytest.mark.asyncio
async def test_analyze_image_timeout(tmp_path, mock_anthropic_client):
    """Test timeout handling in vision service."""
    test_image = tmp_path / "test.jpg"
    test_image.write_bytes(b"fake image data")

    # Mock timeout
    mock_anthropic_client.messages.create = AsyncMock(
        side_effect=asyncio.TimeoutError()
    )

    # Expect VisionAPIError
    with pytest.raises(VisionAPIError, match="timed out"):
        await analyze_image(str(test_image), settings)

# src/tests/test_url_builder.py
def test_build_marketplace_links_book():
    """Test marketplace routing for books."""
    analysis = VisionAnalysisResult(
        object_type="book",
        description="Fiction novel",
        search_queries=[
            SearchQuery(query="roman policier français", confidence=0.9)
        ],
        confidence=0.85
    )

    links = build_marketplace_links(analysis)

    assert len(links) == 1
    assert links[0].marketplace == "abebooks"
    assert "abebooks.fr" in links[0].url
    assert "roman+policier+fran%C3%A7ais" in links[0].url

def test_build_marketplace_links_special_chars():
    """Test URL encoding handles special characters."""
    analysis = VisionAnalysisResult(
        object_type="general",
        description="Tool",
        search_queries=[
            SearchQuery(query="clé à molette 20mm", confidence=0.8)
        ],
        confidence=0.75
    )

    links = build_marketplace_links(analysis)

    # Verify URL encoding
    assert "cl%C3%A9" in links[0].url  # é encoded
    assert "%C3%A0" in links[0].url    # à encoded

# src/tests/test_routes.py
@pytest.mark.asyncio
async def test_analyze_endpoint_success(test_client, mock_vision_service):
    """Test successful image upload and analysis."""
    # Create test file
    files = {"file": ("test.jpg", b"fake image data", "image/jpeg")}

    # Mock service response
    mock_vision_service.analyze_image.return_value = VisionAnalysisResult(...)

    # Make request
    response = await test_client.post("/api/analyze", files=files)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "marketplace_links" in data
    assert data["processing_time_seconds"] < 10

@pytest.mark.asyncio
async def test_analyze_endpoint_file_too_large(test_client):
    """Test file size validation."""
    # Create 15MB fake file (exceeds 10MB limit)
    large_data = b"x" * (15 * 1024 * 1024)
    files = {"file": ("large.jpg", large_data, "image/jpeg")}

    response = await test_client.post("/api/analyze", files=files)

    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()
```

```bash
# Run tests iteratively until passing:
uv run pytest src/tests/ -v --cov=src --cov-report=term-missing

# Target: 80%+ coverage
# If failing:
# 1. Read error message carefully
# 2. Check which assertion failed
# 3. Fix code, not test (unless test is wrong)
# 4. Re-run specific test: uv run pytest src/tests/test_routes.py::test_name -v
```

### Level 3: Integration Test
```bash
# Start the application
uv run uvicorn src.main:app --reload --port 8000

# In browser, open: http://localhost:8000/static/index.html

# Manual test steps:
# 1. Upload a book cover image → Expect: Abebooks.fr links
# 2. Upload clothing photo → Expect: Vinted links
# 3. Upload electronics photo → Expect: Leboncoin links
# 4. Upload very large file (>10MB) → Expect: Error message
# 5. Upload non-image file → Expect: Error message
# 6. Check processing time < 5 seconds for each upload

# Health check:
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# API test with curl:
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_book.jpg" \
  | jq .

# Expected response:
# {
#   "analysis": {
#     "object_type": "book",
#     "description": "...",
#     "search_queries": [...],
#     "confidence": 0.85
#   },
#   "marketplace_links": [
#     {
#       "marketplace": "abebooks",
#       "query": "...",
#       "url": "https://www.abebooks.fr/..."
#     }
#   ],
#   "processing_time_seconds": 3.21
# }
```

## Final Validation Checklist
- [ ] All tests pass: `uv run pytest src/tests/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Code coverage ≥ 80%: `uv run pytest --cov=src --cov-report=html`
- [ ] Manual upload test successful (book, clothing, general items)
- [ ] File validation works (rejects invalid types and oversized files)
- [ ] Generated marketplace URLs are clickable and work in browser
- [ ] Processing time < 5 seconds for typical images
- [ ] Error messages are user-friendly (no raw API errors exposed)
- [ ] Temporary files are cleaned up after processing
- [ ] README includes complete setup and usage instructions
- [ ] .env.example includes all required variables
- [ ] All files ≤ 500 lines (CLAUDE.md requirement)
- [ ] All functions ≤ 50 lines (CLAUDE.md requirement)
- [ ] All lines ≤ 100 characters (CLAUDE.md requirement)

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode API keys - use environment variables with python-dotenv
- ❌ Don't update pyproject.toml directly - always use `uv add` commands
- ❌ Don't skip file validation - check both extension and magic numbers
- ❌ Don't leave temporary files - always cleanup in finally blocks
- ❌ Don't ignore timeouts - set reasonable limits on API calls
- ❌ Don't expose raw API errors to users - provide friendly error messages
- ❌ Don't skip URL encoding - use urllib.parse.quote()
- ❌ Don't test generated URLs manually - include in automated tests
- ❌ Don't use sync functions - FastAPI endpoints must be async
- ❌ Don't exceed file/function line limits from CLAUDE.md

## Confidence Score: 9/10

**High confidence due to:**
- ✅ Clear examples from official documentation (Claude Vision, FastAPI)
- ✅ Well-defined feature requirements with specific marketplace URLs
- ✅ Established project standards in CLAUDE.md
- ✅ Pydantic v2 patterns for structured validation
- ✅ Comprehensive validation gates (linting, tests, integration)
- ✅ Recent 2025 documentation from web search
- ✅ Simple, focused scope (single-page app, clear inputs/outputs)
- ✅ UV package management patterns understood

**Minor uncertainties:**
- ⚠️ Claude Vision API's actual accuracy for diverse object types (will need real-world testing)
- ⚠️ French marketplace URL patterns might have undocumented query parameters (but basic patterns are sufficient for MVP)

**Mitigation strategies:**
- Use confidence scores in VisionAnalysisResult to flag low-confidence identifications
- Include fallback to "general" category (Leboncoin) for ambiguous objects
- Extensive error handling and user-friendly error messages
- Manual testing with diverse image types during validation

This PRP provides sufficient context for one-pass implementation with iterative refinement through the validation loops.

---

## Sources

**Claude Vision API:**
- [Vision - Claude Docs](https://docs.claude.com/en/docs/build-with-claude/vision)
- [Claude API Integration Guide 2025](https://collabnix.com/claude-api-integration-guide-2025-complete-developer-tutorial-with-code-examples/)

**FastAPI:**
- [Request Files - FastAPI](https://fastapi.tiangolo.com/tutorial/request-files/)
- [Uploading Files Using FastAPI](https://betterstack.com/community/guides/scaling-python/uploading-files-using-fastapi/)
- [UploadFile class - FastAPI](https://fastapi.tiangolo.com/reference/uploadfile/)

**Pydantic:**
- [Building product search with Vision API and Pydantic](https://pydantic.dev/articles/llm-vision)
- [Pydantic Documentation](https://docs.pydantic.dev/)
