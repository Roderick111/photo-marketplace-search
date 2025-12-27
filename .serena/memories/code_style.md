# Code Style & Conventions

## Python Style
- Line length: 100 characters (ruff config)
- Python version: 3.13
- Use type hints for all function signatures
- Use double quotes for strings
- Follow PEP8 with ruff enforcement

## Naming Conventions
- Variables/functions: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Private: _leading_underscore

## Pydantic Models
- Use Pydantic v2 syntax
- Use Field() for validation
- Use Literal[] for enums in responses

## Async Patterns
- All service functions are async
- Use aiofiles for file I/O
- Use httpx.AsyncClient for HTTP requests

## Error Handling
- Custom exceptions in src/core/exceptions.py
- Use specific exception types (VisionAPIError, ImageValidationError)
- Log errors with logger before raising

## Logging
- Use module-level logger: `logger = logging.getLogger(__name__)`
- Log INFO for important operations
- Log DEBUG for verbose details
- Log ERROR/WARNING for issues

## Testing
- Use pytest fixtures in conftest.py
- Use pytest.mark.asyncio for async tests
- Mock external APIs (Anthropic, HTTP)
- Test file naming: test_*.py
