"""
Claude Vision API integration service.

Handles image analysis using Claude's vision capabilities to identify
objects and generate marketplace search queries.
"""

import base64
import io
import json
import logging
import re
from pathlib import Path

import aiofiles
import anthropic
from PIL import Image

from src.core.config import Settings
from src.core.exceptions import VisionAPIError
from src.models.responses import VisionAnalysisResult

logger = logging.getLogger(__name__)

# Claude Vision API limit is 5MB for base64, so we target 3.5MB raw to be safe
MAX_BASE64_SIZE = 4 * 1024 * 1024  # 4MB base64 limit (leaves buffer for 5MB API limit)

# Media type mapping for supported image formats
MEDIA_TYPE_MAP: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def get_media_type(image_path: str) -> str:
    """
    Determine media type from file extension.

    Args:
        image_path: Path to the image file.

    Returns:
        MIME type string (e.g., "image/jpeg").

    Raises:
        VisionAPIError: If file extension is not supported.
    """
    ext = Path(image_path).suffix.lower()
    media_type = MEDIA_TYPE_MAP.get(ext)
    if not media_type:
        raise VisionAPIError(f"Unsupported image format: {ext}")
    return media_type


def _resize_image_if_needed(image_bytes: bytes, media_type: str) -> bytes:
    """
    Resize image if base64 encoding would exceed API limit.

    Args:
        image_bytes: Original image bytes.
        media_type: MIME type of the image.

    Returns:
        Image bytes (resized if necessary).
    """
    # Check if base64 would be too large
    base64_size = len(base64.b64encode(image_bytes))
    if base64_size <= MAX_BASE64_SIZE:
        return image_bytes

    logger.info(f"Image too large ({base64_size} bytes base64), resizing...")

    # Open image with Pillow
    img = Image.open(io.BytesIO(image_bytes))

    # Calculate scaling factor to get under limit
    # Base64 is ~1.33x larger than raw, so target raw size accordingly
    target_raw_size = MAX_BASE64_SIZE * 0.75  # ~3MB raw
    current_raw_size = len(image_bytes)
    scale_factor = (target_raw_size / current_raw_size) ** 0.5  # Square root for 2D scaling

    # Resize image
    new_width = int(img.width * scale_factor)
    new_height = int(img.height * scale_factor)
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    logger.info(f"Resized from {img.width}x{img.height} to {new_width}x{new_height}")

    # Convert back to bytes
    output = io.BytesIO()
    img_format = "JPEG" if "jpeg" in media_type else media_type.split("/")[1].upper()
    if img_format == "WEBP":
        img_resized.save(output, format=img_format, quality=85)
    else:
        # Convert RGBA to RGB for JPEG
        if img_resized.mode == "RGBA" and img_format == "JPEG":
            img_resized = img_resized.convert("RGB")
        img_resized.save(output, format=img_format, quality=85)

    return output.getvalue()


def _build_system_prompt() -> str:
    """Build system prompt with JSON schema for structured output."""
    schema = VisionAnalysisResult.model_json_schema()

    return f"""You are an expert at analyzing product images for French marketplace searches.

Your task:
1. Identify the main object in the image
2. Categorize it as one of: book, clothing, electronics, furniture, tools, or general
3. Generate 1-3 descriptive search queries IN FRENCH that would help find similar items

Category guidelines:
- "book": Books, magazines, comics, textbooks
- "clothing": Clothes, shoes, accessories, bags, jewelry
- "electronics": Phones, computers, cameras, TVs, audio equipment
- "furniture": Tables, chairs, sofas, beds, storage
- "tools": Hand tools, power tools, gardening equipment
- "general": Everything else (toys, sports, home decor, etc.)

Return ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Example response:
{{"object_type": "book", "description": "Roman policier français", "search_queries": [{{"query": "livre policier", "confidence": 0.9}}, {{"query": "roman thriller français", "confidence": 0.85}}], "confidence": 0.92}}

IMPORTANT: Return only the JSON object, no additional text or markdown formatting."""


def _extract_json_from_response(text: str) -> str:
    """
    Extract JSON from Claude's response, handling markdown code blocks.

    Args:
        text: Raw response text from Claude.

    Returns:
        Clean JSON string.
    """
    # Try to find JSON in code blocks first
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # Try to find raw JSON object
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json_match.group(0)

    return text.strip()


async def analyze_image(image_path: str, settings: Settings) -> VisionAnalysisResult:
    """
    Analyze image using Claude Vision API and return structured results.

    Args:
        image_path: Path to the image file to analyze.
        settings: Application settings with API configuration.

    Returns:
        VisionAnalysisResult with object type, description, and search queries.

    Raises:
        VisionAPIError: If API call fails or response is invalid.
    """
    logger.info(f"Analyzing image: {image_path}")

    # Get media type from extension
    media_type = get_media_type(image_path)

    # Read and encode image to base64
    try:
        async with aiofiles.open(image_path, "rb") as f:
            image_bytes = await f.read()
    except Exception as e:
        raise VisionAPIError(f"Failed to read image file: {e}") from e

    # Resize if needed to stay under API limit
    image_bytes = _resize_image_if_needed(image_bytes, media_type)

    # Encode to base64 string
    image_data = base64.b64encode(image_bytes).decode("utf-8")

    # Build system prompt with schema
    system_prompt = _build_system_prompt()

    # Create Anthropic client
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    try:
        # Build message content
        message_content: list[dict[str, object]] = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data,
                },
            },
            {
                "type": "text",
                "text": "Analyze this image and identify the object for "
                "French marketplace search. Return JSON only.",
            },
        ]

        # Call Claude Vision API (type: ignore needed for complex anthropic types)
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": message_content,  # type: ignore[typeddict-item]
                }
            ],
        )

        # Extract text from response
        first_block = response.content[0]
        if not hasattr(first_block, "text"):
            raise VisionAPIError("Unexpected response format from API")
        response_text: str = first_block.text  # type: ignore[union-attr]
        logger.debug(f"Raw API response: {response_text}")

        # Extract JSON from response
        json_text = _extract_json_from_response(response_text)

        # Parse and validate with Pydantic
        analysis = VisionAnalysisResult.model_validate_json(json_text)
        logger.info(f"Analysis complete: {analysis.object_type} ({analysis.confidence:.2f})")

        return analysis

    except anthropic.APITimeoutError as e:
        logger.error(f"Vision API timeout: {e}")
        raise VisionAPIError("Vision API request timed out") from e
    except anthropic.APIError as e:
        logger.error(f"Vision API error: {e}")
        raise VisionAPIError(f"Vision API error: {e}") from e
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        raise VisionAPIError(f"Invalid JSON response from API: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error during image analysis: {e}")
        raise VisionAPIError(f"Failed to analyze image: {e}") from e
