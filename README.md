# Photo to Marketplace Search

A web application that converts photos into French marketplace search links using Claude Vision API.

## Features

- **Image Upload**: Drag-and-drop or button-based image upload (JPG, PNG, WebP)
- **AI Object Detection**: Claude Vision API identifies objects in photos
- **Smart Marketplace Routing**:
  - Books → [Abebooks.fr](https://www.abebooks.fr)
  - Clothing → [Vinted](https://www.vinted.fr)
  - Everything else → [Leboncoin](https://www.leboncoin.fr)
- **Fast Processing**: < 5 seconds from upload to results
- **French Search Queries**: AI generates search terms in French

## Quick Start

### Prerequisites

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager
- Anthropic API key

### Installation

1. Clone and navigate to the project:

```bash
cd photo-marketplace-search
```

2. Install dependencies:

```bash
uv sync
```

3. Configure environment:

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

4. Run the application:

```bash
uv run uvicorn src.main:app --reload --port 8000
```

5. Open in browser: http://localhost:8000/static/index.html

## API Endpoints

### `POST /api/analyze`

Upload an image for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**
```json
{
  "analysis": {
    "object_type": "book",
    "description": "Roman policier français",
    "search_queries": [
      {"query": "livre policier", "confidence": 0.9}
    ],
    "confidence": 0.85
  },
  "marketplace_links": [
    {
      "marketplace": "abebooks",
      "query": "livre policier",
      "url": "https://www.abebooks.fr/servlet/SearchResults?kn=livre%20policier&sts=t"
    }
  ],
  "processing_time_seconds": 3.21
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{"status": "healthy"}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest src/tests/test_url_builder.py -v
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check . --fix

# Type checking
uv run mypy src/
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `CLAUDE_MODEL` | Claude model for vision | `claude-sonnet-4-20250514` |
| `MAX_UPLOAD_SIZE_MB` | Max file size in MB | `10` |
| `UPLOAD_DIR` | Temp upload directory | `uploads` |
| `VISION_API_TIMEOUT` | API timeout in seconds | `30` |

## Marketplace Routing

| Object Type | Marketplace | URL Pattern |
|-------------|-------------|-------------|
| book | Abebooks.fr | `/servlet/SearchResults?kn={query}` |
| clothing | Vinted | `/catalog?search_text={query}` |
| electronics | Leboncoin | `/recherche?text={query}` |
| furniture | Leboncoin | `/recherche?text={query}` |
| tools | Leboncoin | `/recherche?text={query}` |
| general | Leboncoin | `/recherche?text={query}` |

## Project Structure

```
photo-marketplace-search/
├── src/
│   ├── api/            # FastAPI routes
│   ├── core/           # Configuration and exceptions
│   ├── models/         # Pydantic models
│   ├── services/       # Business logic
│   ├── static/         # Frontend (HTML/CSS/JS)
│   └── tests/          # Test suite
├── uploads/            # Temp upload directory
├── pyproject.toml      # UV project config
└── .env.example        # Environment template
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

Ensure your `.env` file exists and contains a valid API key:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### "File too large"

The maximum upload size is 10MB by default. Compress your image or adjust `MAX_UPLOAD_SIZE_MB`.

### "Invalid file type"

Only JPG, JPEG, PNG, and WebP images are supported.

### "Vision API request timed out"

Increase `VISION_API_TIMEOUT` or check your network connection.

## License

MIT
