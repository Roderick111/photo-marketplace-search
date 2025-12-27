# Development Commands

## Package Management (UV - NOT pip)
```bash
uv sync                    # Install dependencies
uv add package_name        # Add dependency
uv add --dev package_name  # Add dev dependency
uv remove package_name     # Remove dependency
```

## Running the Application
```bash
uv run uvicorn src.main:app --reload --port 8000
```
Access at: http://localhost:8000/static/index.html

## Testing
```bash
uv run pytest                        # Run all tests
uv run pytest src/tests/ -v          # Verbose output
uv run pytest --cov=src              # With coverage
uv run pytest src/tests/test_file.py # Specific file
```

## Linting & Formatting
```bash
uv run ruff check .                  # Check linting
uv run ruff check --fix .            # Auto-fix issues
uv run ruff format .                 # Format code
```

## Type Checking
```bash
uv run mypy src/                     # Type check
```

## Full Validation (run before commits)
```bash
uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest -v
```
