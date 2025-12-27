# Photo Marketplace Search - Project Overview

## Purpose
Web application that converts photos into French marketplace search links using Claude Vision API.

## Tech Stack
- **Language**: Python 3.13
- **Framework**: FastAPI (async)
- **Package Manager**: UV (not pip)
- **Validation**: Pydantic v2, pydantic-settings
- **API**: Anthropic Claude Vision API
- **Image Processing**: Pillow
- **Async I/O**: aiofiles
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Linting**: ruff
- **Type Checking**: mypy

## Project Structure
```
photo-marketplace-search/
├── src/
│   ├── api/routes.py          # FastAPI endpoints
│   ├── core/config.py         # Settings with pydantic-settings
│   ├── core/exceptions.py     # Custom exceptions
│   ├── models/responses.py    # Pydantic response models
│   ├── services/
│   │   ├── vision_service.py  # Claude Vision API integration
│   │   ├── url_builder.py     # Marketplace URL generation
│   │   └── link_validator.py  # Link validation (validates URLs have results)
│   ├── static/                # Frontend HTML/CSS/JS
│   └── tests/                 # Test files
└── pyproject.toml
```

## Key Files
- `src/api/routes.py` - Main endpoint: POST /api/analyze
- `src/services/vision_service.py` - Claude API calls with image resizing
- `src/services/url_builder.py` - Routes to Abebooks/Vinted/Leboncoin
- `src/core/config.py` - Environment configuration
