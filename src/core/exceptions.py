"""
Custom exceptions for the Photo to Marketplace Search application.

Provides specific exception types for different failure modes,
enabling proper error handling and user-friendly error messages.
"""


class VisionAPIError(Exception):
    """
    Raised when Claude Vision API fails.

    This can occur due to:
    - API rate limits
    - Network issues
    - Invalid image format
    - Timeout during processing
    """

    def __init__(self, message: str = "Vision API request failed"):
        self.message = message
        super().__init__(self.message)


class ImageValidationError(Exception):
    """
    Raised when uploaded image fails validation.

    This can occur due to:
    - File too large (exceeds max_upload_size_mb)
    - Invalid file type (not in allowed_extensions)
    - Corrupted image data
    - Failed magic number validation
    """

    def __init__(self, message: str = "Image validation failed"):
        self.message = message
        super().__init__(self.message)


class MarketplaceRoutingError(Exception):
    """
    Raised when marketplace routing fails.

    This can occur due to:
    - Unknown object type
    - URL encoding failures
    - Invalid search query
    """

    def __init__(self, message: str = "Marketplace routing failed"):
        self.message = message
        super().__init__(self.message)
