"""
translator.py - Translation Engine Module
------------------------------------------
Core translation engine for the CodeAlpha Language Translation Tool.
Interacts with the MyMemory Translation API (https://mymemory.translated.net).

Features:
- Full English <-> Urdu support with RTL detection.
- Autodetection of source languages.
- Safe sentence-level text chunking for texts exceeding 500 characters.
- Robust error classification (Validation, Network, Timeout, Rate Limit, API errors).
- HTML entity unescaping for clean output.
- Zero-cost identical language bypass.
"""

from dataclasses import dataclass
import html
import re
from typing import Dict, List, Optional
import requests

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------

API_ENDPOINT = "https://api.mymemory.translated.net/get"
DEFAULT_TIMEOUT_SECONDS = 10

# MyMemory's verified single-request limit is 500 bytes/chars.
MAX_SINGLE_CHUNK_CHARS = 450
# Application-level safety cap to prevent accidental quota exhaustion.
MAX_TOTAL_CHARS = 2500

# Curated catalog of verified languages supported by MyMemory
# Format: code -> (English Name, Native/Local Name, is_rtl)
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "autodetect": {"name": "Auto Detect", "native": "Auto Detect", "rtl": False},
    "en": {"name": "English", "native": "English", "rtl": False},
    "ur": {"name": "Urdu", "native": "اردو", "rtl": True},
    "ar": {"name": "Arabic", "native": "العربية", "rtl": True},
    "es": {"name": "Spanish", "native": "Español", "rtl": False},
    "fr": {"name": "French", "native": "Français", "rtl": False},
    "de": {"name": "German", "native": "Deutsch", "rtl": False},
    "hi": {"name": "Hindi", "native": "हिन्दी", "rtl": False},
    "zh-CN": {"name": "Chinese (Simplified)", "native": "简体中文", "rtl": False},
    "ja": {"name": "Japanese", "native": "日本語", "rtl": False},
    "ru": {"name": "Russian", "native": "Русский", "rtl": False},
    "tr": {"name": "Turkish", "native": "Türkçe", "rtl": False},
    "it": {"name": "Italian", "native": "Italiano", "rtl": False},
    "pt": {"name": "Portuguese", "native": "Português", "rtl": False},
    "ko": {"name": "Korean", "native": "한국어", "rtl": False},
    "fa": {"name": "Persian", "native": "فارسی", "rtl": True},
    "ps": {"name": "Pashto", "native": "پښتو", "rtl": True},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ / پنجابی", "rtl": False},
    "bn": {"name": "Bengali", "native": "বাংলা", "rtl": False},
}

RTL_LANGUAGE_CODES = {"ur", "ar", "fa", "ps", "he"}


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class TranslationError(Exception):
    """Base exception for all translation-related errors."""
    pass


class ValidationError(TranslationError):
    """Raised when input text, length, or language codes are invalid."""
    pass


class NetworkError(TranslationError):
    """Raised when internet connection is lost or DNS lookup fails."""
    pass


class RequestTimeoutError(TranslationError):
    """Raised when the translation API fails to respond within the timeout."""
    pass


class RateLimitError(TranslationError):
    """Raised when API daily quota or rate limit has been exceeded."""
    pass


class APIResponseError(TranslationError):
    """Raised when the API returns an unexpected status, payload, or server error."""
    pass


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class TranslationResult:
    """Structured result returned by the translation engine."""
    translated_text: str
    source_language: str
    target_language: str
    detected_language: Optional[str] = None
    match_score: float = 0.0
    is_identical: bool = False
    is_rtl: bool = False
    chunks_count: int = 1


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def is_rtl(language_code: str) -> bool:
    """Check if the given language code uses a Right-to-Left writing script."""
    clean_code = (language_code or "").strip().lower()
    return clean_code in RTL_LANGUAGE_CODES


def split_text_into_chunks(text: str, max_chars: int = MAX_SINGLE_CHUNK_CHARS) -> List[str]:
    """
    Split text into safe chunks without breaking words or sentences mid-character.
    Respects sentence boundaries (., !, ?, \n, Urdu full stop '۔').
    """
    if len(text) <= max_chars:
        return [text]

    chunks: List[str] = []
    # Pattern to match sentence boundaries preserving delimiters
    sentence_pattern = re.compile(r'(.*?[.!?۔\n]+(?:\s+|$)|.+?$)', re.DOTALL)
    sentences = [m.group(0) for m in sentence_pattern.finditer(text) if m.group(0)]

    current_chunk = ""
    for sentence in sentences:
        if not sentence:
            continue

        # If a single sentence is larger than max_chars, split by words
        if len(sentence) > max_chars:
            words = sentence.split(" ")
            for word in words:
                word_with_space = word + " "
                if len(current_chunk) + len(word_with_space) <= max_chars:
                    current_chunk += word_with_space
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = word_with_space
            continue

        # Normal accumulation
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]


# ---------------------------------------------------------------------------
# Core Translation Functions
# ---------------------------------------------------------------------------

def _call_mymemory_api(
    text: str,
    source_lang: str,
    target_lang: str,
    email: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict:
    """
    Execute a single low-level HTTP GET call to the MyMemory endpoint.
    Parses and verifies the JSON payload.
    """
    # Construct language pair query parameter (e.g., 'en|ur' or 'autodetect|en')
    src = "autodetect" if source_lang == "autodetect" else source_lang.strip()
    tgt = target_lang.strip()
    langpair = f"{src}|{tgt}"

    params = {
        "q": text,
        "langpair": langpair,
    }

    if email and email.strip():
        params["de"] = email.strip()

    try:
        response = requests.get(
            API_ENDPOINT,
            params=params,
            timeout=timeout,
            headers={"User-Agent": "CodeAlpha-TranslationTool/1.0 (Educational Project)"},
        )
    except requests.exceptions.Timeout as exc:
        raise RequestTimeoutError(
            f"The translation server timed out after {timeout} seconds. "
            "Please check your internet connection or try again shortly."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise NetworkError(
            "Could not connect to the translation service. "
            "Please verify that your computer is connected to the internet."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise NetworkError(f"Network error during translation request: {exc}") from exc

    # Parse JSON body
    try:
        data = response.json()
    except ValueError as exc:
        raise APIResponseError(
            f"Received non-JSON response from server (HTTP {response.status_code})."
        ) from exc

    # Inspect HTTP status code and API-level payload
    response_status = data.get("responseStatus") or response.status_code
    response_details = str(data.get("responseDetails") or "")
    quota_finished = data.get("quotaFinished", False)

    # Detect quota limits
    if response_status == 429 or quota_finished or "YOU USED ALL YOUR FREE QUOTA" in response_details.upper():
        raise RateLimitError(
            "Daily free translation quota reached for MyMemory API. "
            "Free tier resets daily. Consider passing an email address in settings to extend your quota."
        )

    if response_status == 403:
        raise RateLimitError(
            f"Access denied by translation service: {response_details or 'Quota exceeded or blocked'}"
        )

    if response_status >= 500 or response.status_code >= 500:
        raise APIResponseError(
            f"Translation server encountered an internal error (Status {response_status}). "
            f"Details: {response_details}"
        )

    if response.status_code != 200 and response_status not in (200, "200"):
        raise APIResponseError(
            f"Translation API returned status {response_status}: {response_details or 'Unknown error'}"
        )

    return data


def translate(
    text: str,
    source_lang: str,
    target_lang: str,
    email: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> TranslationResult:
    """
    Main entry point for translating text.

    Args:
        text: The source text to translate.
        source_lang: ISO language code (e.g. 'en', 'ur', 'es') or 'autodetect'.
        target_lang: Target ISO language code (e.g. 'ur', 'en', 'fr').
        email: Optional contact email to raise daily quota to 50,000 characters.
        timeout: Request timeout in seconds.

    Returns:
        TranslationResult containing translated text, detected language, and metadata.

    Raises:
        ValidationError: If input is invalid, empty, or exceeds limit.
        NetworkError: If offline or connection fails.
        RequestTimeoutError: If request times out.
        RateLimitError: If API quota is finished.
        APIResponseError: If server responds with an error.
    """
    # 1. Input Validation: Check empty or whitespace-only
    if text is None:
        raise ValidationError("Input text cannot be None.")

    stripped_text = text.strip()
    if not stripped_text:
        raise ValidationError("Input text cannot be empty or contain only whitespace.")

    # 2. Input Validation: Text Length Limit
    if len(text) > MAX_TOTAL_CHARS:
        raise ValidationError(
            f"Text length ({len(text)} characters) exceeds the maximum allowed limit "
            f"of {MAX_TOTAL_CHARS} characters for this educational tool."
        )

    # 3. Input Validation: Language codes
    src = (source_lang or "").strip()
    tgt = (target_lang or "").strip()

    if not src:
        raise ValidationError("Source language must be specified.")
    if not tgt:
        raise ValidationError("Target language must be specified.")

    if tgt == "autodetect":
        raise ValidationError("Target language cannot be 'Auto Detect'. Please choose a specific target language.")

    if src != "autodetect" and src not in SUPPORTED_LANGUAGES:
        raise ValidationError(f"Unsupported source language code: '{src}'.")
    if tgt not in SUPPORTED_LANGUAGES:
        raise ValidationError(f"Unsupported target language code: '{tgt}'.")

    # 4. Shortcut: Identical source and target languages
    if src == tgt:
        return TranslationResult(
            translated_text=text,
            source_language=src,
            target_language=tgt,
            detected_language=src,
            match_score=1.0,
            is_identical=True,
            is_rtl=is_rtl(tgt),
            chunks_count=0,
        )

    # 5. Chunking for long text
    chunks = split_text_into_chunks(text, max_chars=MAX_SINGLE_CHUNK_CHARS)

    translated_pieces: List[str] = []
    detected_language: Optional[str] = None
    scores: List[float] = []

    for index, chunk in enumerate(chunks):
        if not chunk.strip():
            continue

        raw_result = _call_mymemory_api(
            text=chunk,
            source_lang=src,
            target_lang=tgt,
            email=email,
            timeout=timeout,
        )

        response_data = raw_result.get("responseData") or {}
        translated_chunk = response_data.get("translatedText")

        if translated_chunk is None:
            raise APIResponseError(
                f"API response missing 'translatedText' field for chunk {index + 1}."
            )

        # Unescape HTML entities (e.g. &#39; -> ', &quot; -> ", &amp; -> &)
        clean_chunk = html.unescape(translated_chunk)
        translated_pieces.append(clean_chunk)

        # Extract detected language from the first chunk if available
        if index == 0:
            detected_language = response_data.get("detectedLanguage")

        # Capture match quality score
        match_score = response_data.get("match", 0.0)
        if isinstance(match_score, (int, float)):
            scores.append(float(match_score))

    # Join translated pieces cleanly
    final_translation = " ".join(translated_pieces) if len(chunks) > 1 else (translated_pieces[0] if translated_pieces else "")
    avg_score = sum(scores) / len(scores) if scores else 0.0

    return TranslationResult(
        translated_text=final_translation,
        source_language=src,
        target_language=tgt,
        detected_language=detected_language,
        match_score=round(avg_score, 2),
        is_identical=False,
        is_rtl=is_rtl(tgt),
        chunks_count=len(chunks),
    )


def main(argv=None) -> int:
    """CLI entry point for translating text directly from command line."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="CodeAlpha Language Translation Tool (CLI)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("text", nargs="?", default="", help="Text to translate (or pass via stdin)")
    parser.add_argument("-t", "--target", default="ur", help="Target language code (e.g. ur, es, fr, ar)")
    parser.add_argument("-s", "--source", default="autodetect", help="Source language code (default: autodetect)")
    parser.add_argument("--email", default=None, help="Optional email for extended daily quota")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="Timeout in seconds")
    parser.add_argument("--list-languages", action="store_true", help="List all supported languages")

    args = parser.parse_args(argv)

    if args.list_languages:
        print("\nSupported Languages:")
        for code, info in SUPPORTED_LANGUAGES.items():
            rtl_flag = " [RTL]" if info.get("rtl") else ""
            native_str = f" ({info.get('native', '')})" if info.get("native") else ""
            print(f"  {code:10} : {info['name']}{native_str}{rtl_flag}")
        return 0

    input_text = args.text
    if not input_text:
        is_tty = True
        try:
            is_tty = sys.stdin.isatty()
        except Exception:
            is_tty = True

        if not is_tty:
            try:
                input_text = sys.stdin.read().strip()
            except (OSError, ValueError):
                input_text = ""

        if not input_text:
            parser.print_help()
            return 1

    try:
        res = translate(
            text=input_text,
            source_lang=args.source,
            target_lang=args.target,
            email=args.email,
            timeout=args.timeout,
        )
        print(f"\n[Source ({res.source_language})]: {input_text}")
        print(f"[Target ({res.target_language})]: {res.translated_text}")
        if res.detected_language:
            print(f"[Detected]: {res.detected_language}")
        if res.match_score > 0:
            print(f"[Quality Match]: {int(res.match_score * 100)}%")
        return 0
    except TranslationError as err:
        print(f"\n[Error]: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
