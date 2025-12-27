"""
API routes for the Photo to Marketplace Search application.

Provides endpoints for image upload and analysis, health checks,
and proper error handling for all failure modes.
"""

import logging
import os
import time
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.core.config import Settings, get_settings
from src.core.exceptions import ImageValidationError, VisionAPIError
from src.models.responses import HealthResponse, MarketplaceSearchResponse
from src.services import (
    link_validator,
    url_builder,
    vision_service,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Magic numbers for image file validation
IMAGE_MAGIC_NUMBERS: dict[bytes, str] = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # WebP starts with RIFF
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
}


async def validate_image_magic_numbers(file: UploadFile) -> str:
    """
    Validate image by checking magic numbers (file signature).

    Args:
        file: Uploaded file to validate.

    Returns:
        Detected MIME type based on magic numbers.

    Raises:
        ImageValidationError: If file is not a valid image.
    """
    # Read first 8 bytes for magic number check
    header = await file.read(8)
    await file.seek(0)  # Reset file position

    for magic, mime_type in IMAGE_MAGIC_NUMBERS.items():
        if header.startswith(magic):
            return mime_type

    # Special check for WebP (RIFF....WEBP format)
    if header[:4] == b"RIFF" and len(header) >= 8:
        # Read more to check for WEBP signature
        extended_header = await file.read(12)
        await file.seek(0)
        if extended_header[8:12] == b"WEBP":
            return "image/webp"

    raise ImageValidationError("File is not a valid image (invalid magic numbers)")


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse indicating service is healthy.
    """
    return HealthResponse(status="healthy")


@router.post("/api/analyze", response_model=MarketplaceSearchResponse)
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
) -> MarketplaceSearchResponse:
    """
    Analyze uploaded image and return marketplace search links.

    Args:
        file: Uploaded image file (JPG, PNG, JPEG, or WebP).
        settings: Application settings (injected).

    Returns:
        MarketplaceSearchResponse with analysis and search links.

    Raises:
        HTTPException: 400 for validation errors, 503 for API failures.
    """
    start_time = time.time()
    temp_path: str | None = None

    try:
        # Validate file size
        max_size = settings.max_upload_size_mb * 1024 * 1024
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start

        if file_size > max_size:
            raise ImageValidationError(
                f"File too large: {file_size / (1024 * 1024):.1f}MB "
                f"(max {settings.max_upload_size_mb}MB)"
            )

        if file_size == 0:
            raise ImageValidationError("Empty file uploaded")

        # Validate file extension
        if not file.filename:
            raise ImageValidationError("No filename provided")

        ext = Path(file.filename).suffix.lower()
        if ext not in settings.allowed_extensions:
            raise ImageValidationError(
                f"Invalid file type: {ext}. Allowed: {', '.join(settings.allowed_extensions)}"
            )

        # Validate magic numbers for security
        await validate_image_magic_numbers(file)

        # Ensure upload directory exists
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)

        # Save with UUID filename to prevent collisions
        temp_filename = f"{uuid.uuid4()}{ext}"
        temp_path = str(upload_dir / temp_filename)

        # Save file asynchronously
        content = await file.read()
        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(content)

        logger.info(f"Saved upload to: {temp_path} ({file_size} bytes)")

        # Analyze image with Claude Vision API
        analysis = await vision_service.analyze_image(temp_path, settings)

        # Build marketplace links
        links = url_builder.build_marketplace_links(analysis)

        # Validate links (filter out those with no results)
        if settings.link_validation_enabled:
            links = await link_validator.validate_marketplace_links(
                links, settings.link_validation_timeout
            )

        # Calculate processing time
        processing_time = time.time() - start_time

        logger.info(f"Analysis complete in {processing_time:.2f}s")

        return MarketplaceSearchResponse(
            analysis=analysis,
            marketplace_links=links,
            processing_time_seconds=round(processing_time, 2),
        )

    except ImageValidationError as e:
        logger.warning(f"Image validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

    except VisionAPIError as e:
        logger.error(f"Vision API failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Image analysis failed. Please try again later.",
        ) from e

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred.",
        ) from e

    finally:
        # Always cleanup temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.debug(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                logger.error(f"Failed to delete temp file: {e}")
