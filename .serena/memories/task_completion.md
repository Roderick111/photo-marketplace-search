# Task Completion Checklist

Before considering any task complete, run these validations:

## 1. Format & Lint
```bash
uv run ruff format .
uv run ruff check --fix .
```
Expected: No errors

## 2. Type Check
```bash
uv run mypy src/
```
Expected: No errors (warnings OK with current config)

## 3. Tests
```bash
uv run pytest src/tests/ -v
```
Expected: All tests pass

## 4. Manual Verification (if UI changes)
- Start server: `uv run uvicorn src.main:app --reload`
- Test in browser: http://localhost:8000/static/index.html
- Upload an image and verify results

## Quick One-Liner
```bash
uv run ruff format . && uv run ruff check --fix . && uv run mypy src/ && uv run pytest -v
```

## Before Git Commit
- Ensure .env is in .gitignore (contains API key)
- Don't commit .coverage, __pycache__, .mypy_cache
