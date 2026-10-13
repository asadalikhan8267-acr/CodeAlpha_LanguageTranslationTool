"""
tests/test_translation.py - Unit Test Suite
--------------------------------------------
Automated unit tests for translator.py using Pytest and unittest.mock.
All external HTTP requests are mocked so tests run without an internet
connection and without consuming API quotas.
"""

import unittest
from unittest.mock import MagicMock, patch
import pytest
import requests

import translator
from translator import (
    APIResponseError,
    NetworkError,
    RateLimitError,
    RequestTimeoutError,
    TranslationResult,
    ValidationError,
    is_rtl,
    split_text_into_chunks,
    translate,
)


class TestInputValidation(unittest.TestCase):
    """Test suite for input verification and parameter validation."""

    def test_empty_string_raises_validation_error(self):
        """Reject empty string input."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            translate("", "en", "ur")

    def test_whitespace_only_raises_validation_error(self):
        """Reject whitespace-only input."""
        with pytest.raises(ValidationError, match="whitespace"):
            translate("    \n\t   ", "en", "ur")

    def test_none_input_raises_validation_error(self):
        """Reject None as input."""
        with pytest.raises(ValidationError, match="cannot be None"):
            translate(None, "en", "ur")  # type: ignore

    def test_text_exceeding_max_limit_raises_validation_error(self):
        """Reject text exceeding the maximum safety character limit."""
        oversized_text = "a" * (translator.MAX_TOTAL_CHARS + 10)
        with pytest.raises(ValidationError, match="exceeds the maximum allowed limit"):
            translate(oversized_text, "en", "ur")

    def test_unsupported_source_language_raises_validation_error(self):
        """Reject unknown/unsupported source language codes."""
        with pytest.raises(ValidationError, match="Unsupported source language code"):
            translate("Hello", "invalid_lang_code", "ur")

    def test_unsupported_target_language_raises_validation_error(self):
        """Reject unknown/unsupported target language codes."""
        with pytest.raises(ValidationError, match="Unsupported target language code"):
            translate("Hello", "en", "invalid_target_code")

    def test_target_language_cannot_be_autodetect(self):
        """Target language cannot be 'autodetect'."""
        with pytest.raises(ValidationError, match="Target language cannot be 'Auto Detect'"):
            translate("Hello", "en", "autodetect")


class TestIdenticalLanguagesAndRTL(unittest.TestCase):
    """Test identical language shortcut and RTL detection."""

    def test_identical_source_and_target_skips_network(self):
        """When source and target match, return input directly without HTTP call."""
        result = translate("Hello world", "en", "en")
        self.assertTrue(result.is_identical)
        self.assertEqual(result.translated_text, "Hello world")
        self.assertEqual(result.chunks_count, 0)
        self.assertFalse(result.is_rtl)

    def test_identical_urdu_preserves_rtl_flag(self):
        """When source and target are both Urdu, return text with is_rtl=True."""
        urdu_text = "ہیلو دنیا"
        result = translate(urdu_text, "ur", "ur")
        self.assertTrue(result.is_identical)
        self.assertEqual(result.translated_text, urdu_text)
        self.assertTrue(result.is_rtl)

    def test_is_rtl_helper(self):
        """Verify RTL script detection for Urdu, Arabic, Persian, etc."""
        self.assertTrue(is_rtl("ur"))
        self.assertTrue(is_rtl("ar"))
        self.assertTrue(is_rtl("fa"))
        self.assertFalse(is_rtl("en"))
        self.assertFalse(is_rtl("fr"))
        self.assertFalse(is_rtl("de"))


class TestMockedAPITranslation(unittest.TestCase):
    """Test API response handling using mocks to avoid internet/quota dependencies."""

    @patch("requests.get")
    def test_successful_english_to_urdu_translation(self, mock_get):
        """Simulate a successful English to Urdu translation response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseData": {
                "translatedText": "ہیلو دنیا",
                "match": 0.85,
                "detectedLanguage": "en",
            },
            "responseStatus": 200,
            "quotaFinished": False,
        }
        mock_get.return_value = mock_response

        result = translate("Hello world", "en", "ur")
        self.assertEqual(result.translated_text, "ہیلو دنیا")
        self.assertTrue(result.is_rtl)
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "ur")
        self.assertEqual(result.match_score, 0.85)

    @patch("requests.get")
    def test_unescapes_html_entities_in_translated_text(self, mock_get):
        """Ensure HTML entities such as &#39; and &quot; are converted to proper characters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseData": {
                "translatedText": "Don&#39;t worry, it&quot;s safe &amp; sound",
                "match": 0.90,
            },
            "responseStatus": 200,
            "quotaFinished": False,
        }
        mock_get.return_value = mock_response

        result = translate("Don't worry", "en", "es")
        self.assertEqual(result.translated_text, 'Don\'t worry, it"s safe & sound')

    @patch("requests.get")
    def test_network_connection_error_raises_custom_exception(self, mock_get):
        """Simulate loss of internet connectivity."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")

        with pytest.raises(NetworkError, match="Could not connect to the translation service"):
            translate("Hello", "en", "ur")

    @patch("requests.get")
    def test_request_timeout_raises_custom_exception(self, mock_get):
        """Simulate server request timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(RequestTimeoutError, match="timed out"):
            translate("Hello", "en", "ur")

    @patch("requests.get")
    def test_rate_limit_429_raises_custom_exception(self, mock_get):
        """Simulate daily quota limit reached."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "responseStatus": 429,
            "responseDetails": "MYMEMORY WARNING: YOU USED ALL YOUR FREE QUOTA FOR TODAY",
            "quotaFinished": True,
        }
        mock_get.return_value = mock_response

        with pytest.raises(RateLimitError, match="Daily free translation quota reached"):
            translate("Hello", "en", "ur")

    @patch("requests.get")
    def test_server_500_error_raises_api_response_error(self, mock_get):
        """Simulate internal server error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "responseStatus": 500,
            "responseDetails": "Internal Server Error",
        }
        mock_get.return_value = mock_response

        with pytest.raises(APIResponseError, match="internal error"):
            translate("Hello", "en", "ur")

    @patch("requests.get")
    def test_malformed_json_response_raises_api_response_error(self, mock_get):
        """Simulate server returning invalid non-JSON output."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(APIResponseError, match="non-JSON response"):
            translate("Hello", "en", "ur")

    @patch("requests.get")
    def test_missing_translated_text_field_raises_api_response_error(self, mock_get):
        """Simulate server response missing the 'translatedText' field."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseData": {},
            "responseStatus": 200,
        }
        mock_get.return_value = mock_response

        with pytest.raises(APIResponseError, match="missing 'translatedText' field"):
            translate("Hello", "en", "ur")


class TestChunkingAndLongText(unittest.TestCase):
    """Test text splitting for long inputs exceeding 450 characters."""

    def test_short_text_stays_single_chunk(self):
        """Short sentences should not be split."""
        text = "This is a short single sentence."
        chunks = split_text_into_chunks(text, max_chars=450)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_long_multisentence_text_splits_cleanly(self):
        """Long text with sentences should split across sentence boundaries."""
        sentence = "This is a meaningful complete test sentence for chunk verification. "
        long_text = sentence * 12  # ~816 characters
        chunks = split_text_into_chunks(long_text, max_chars=400)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 450)

    @patch("requests.get")
    def test_multichunk_translation_assembles_correctly(self, mock_get):
        """Ensure multi-chunk input issues sequential requests and joins text."""
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {
            "responseData": {"translatedText": "Part One Translation.", "match": 0.8},
            "responseStatus": 200,
        }

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            "responseData": {"translatedText": "Part Two Translation.", "match": 0.8},
            "responseStatus": 200,
        }

        mock_get.side_effect = [mock_response1, mock_response2]

        # Construct input text longer than MAX_SINGLE_CHUNK_CHARS (450)
        chunk1 = "A" * 300 + ". "
        chunk2 = "B" * 300 + "."
        text = chunk1 + chunk2

        result = translate(text, "en", "fr")
        self.assertGreater(result.chunks_count, 1)
        self.assertIn("Part One Translation.", result.translated_text)
        self.assertIn("Part Two Translation.", result.translated_text)



class TestPackageAndCLI(unittest.TestCase):
    """Test suite for package exports and CLI entrypoint functionality."""

    def test_package_exports_exist(self):
        """Verify that language_translation_tool exposes all public symbols."""
        import language_translation_tool as pkg

        assert hasattr(pkg, "__version__")
        assert hasattr(pkg, "translate")
        assert hasattr(pkg, "TranslationResult")
        assert hasattr(pkg, "ValidationError")
        assert hasattr(pkg, "SUPPORTED_LANGUAGES")
        assert hasattr(pkg, "main")

    def test_root_translator_shim_has_all_symbols(self):
        """Verify backwards compatibility shim in root translator.py."""
        import translator as shim

        assert hasattr(shim, "translate")
        assert hasattr(shim, "TranslationResult")
        assert hasattr(shim, "is_rtl")
        assert hasattr(shim, "split_text_into_chunks")
        assert hasattr(shim, "main")

    def test_cli_list_languages(self, capsys=None):
        """Verify CLI --list-languages prints languages and returns 0."""
        from language_translation_tool.translator import main

        ret = main(["--list-languages"])
        assert ret == 0

    @patch("language_translation_tool.translator._call_mymemory_api")
    def test_cli_translate_success(self, mock_api):
        """Verify CLI translates text and returns 0."""
        mock_api.return_value = {
            "responseData": {
                "translatedText": "ہیلو دنیا",
                "match": 0.95,
                "detectedLanguage": "en",
            },
            "responseStatus": 200,
        }
        from language_translation_tool.translator import main

        ret = main(["Hello world", "--target", "ur"])
        assert ret == 0

    def test_cli_missing_text_returns_error(self):
        """Verify CLI with no input returns error code 1."""
        from language_translation_tool.translator import main

        ret = main([])
        assert ret == 1
