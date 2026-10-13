"""
language_translation_tool
=========================
Core package for the CodeAlpha Language Translation Tool.
Provides robust text translation, right-to-left (RTL) script detection,
sentence-level chunking, and error classification via the MyMemory API.
"""

from .translator import (
    TranslationError,
    ValidationError,
    NetworkError,
    RequestTimeoutError,
    RateLimitError,
    APIResponseError,
    TranslationResult,
    SUPPORTED_LANGUAGES,
    RTL_LANGUAGE_CODES,
    is_rtl,
    split_text_into_chunks,
    translate,
    main,
)

__version__ = "1.0.0"
__all__ = [
    "TranslationError",
    "ValidationError",
    "NetworkError",
    "RequestTimeoutError",
    "RateLimitError",
    "APIResponseError",
    "TranslationResult",
    "SUPPORTED_LANGUAGES",
    "RTL_LANGUAGE_CODES",
    "is_rtl",
    "split_text_into_chunks",
    "translate",
    "main",
    "__version__",
]
