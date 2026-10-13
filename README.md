# CodeAlpha Artificial Intelligence Internship
## Task 1: Language Translation Tool

An interactive, responsive, and lightweight **Language Translation Tool** built with Python and Streamlit. The application performs real-time multilingual translation using the public **MyMemory Translation API**, featuring native Right-to-Left (RTL) script rendering for **Urdu**, sentence-level chunking for long texts, defensive error handling, a dedicated CLI mode, and a comprehensive 26-test automated test suite.

---

## 1. Project Overview & Objectives

- **Organization:** CodeAlpha Artificial Intelligence Internship
- **Role:** AI & Software Engineering Intern
- **Task:** 1 - Language Translation Tool
- **Primary Goal:** Develop a clean, reliable, and user-friendly software tool demonstrating real-world REST API integration, modular architecture, input validation, defensive error handling, and automated unit testing without relying on paid services or heavy machine-learning packages.
- **Repository:** [https://github.com/asadalikhan8267-acr/CodeAlpha_LanguageTranslationTool](https://github.com/asadalikhan8267-acr/CodeAlpha_LanguageTranslationTool)

---

## 2. Key Features

- **Real-Time Multilingual Translation:** Translates text between English, Urdu, Arabic, Spanish, French, German, Hindi, Chinese, and other global languages using live REST API queries.
- **English <-> Urdu Specialization:** Full support for Urdu typography and Nastaliq-style script with proper **Right-to-Left (RTL)** text formatting.
- **Auto-Detection:** Automatically identifies the source language if selected.
- **Sentence-Level Chunking:** Automatically divides longer paragraphs (over 450 characters) along sentence boundaries (`.`, `!`, `?`, `۔`) to respect API limits without breaking words mid-character.
- **Zero-Cost Identical Language Bypass:** If the source and target languages are identical, the tool bypasses the external API, avoiding unnecessary network traffic and saving quota.
- **Dual Interface (Web GUI & CLI):**
  - **Web GUI:** Interactive Streamlit interface with a responsive two-column layout, live character counters, dynamic quality badges, language swapping, one-click text clearing, and copyable text containers.
  - **CLI Mode:** Command-line tool for headless environments, batch automation, and terminal translation (`python translator.py "Hello world" --target ur`).
- **Defensive Error Handling:** Clear, friendly alerts for network outages, request timeouts, daily quota exhaustion, or invalid input - preventing raw technical tracebacks from ever reaching the user.
- **Automated Unit Testing:** 26 automated unit tests using `pytest` and `unittest.mock` to verify validation, error catching, chunking, and CLI execution without requiring internet access or consuming API quota.
- **1-Click Windows Launchers:** Dedicated `.bat` scripts to launch the web app, run unit tests, and push updates with a single double-click.

---

## 3. Technology Stack

- **Programming Language:** Python 3.10
- **User Interface Framework:** Streamlit (`streamlit>=1.30.0`)
- **HTTP Client:** Requests (`requests>=2.31.0`)
- **Testing Framework:** Pytest (`pytest>=8.0.0`) & Python standard library `unittest.mock`
- **Packaging:** Setuptools & `pyproject.toml`
- **Translation Provider:** MyMemory Translation API (Translated.net)

---

## 4. Project Folder Structure

```text
CodeAlpha_LanguageTranslationTool/
|-- language_translation_tool/        # Modular core package
|   |-- __init__.py                   # Package exports and version metadata
|   `-- translator.py                 # Core translation engine, API client & CLI
|-- tests/
|   |-- __init__.py                   # Test package marker
|   `-- test_translation.py           # 26 automated unit tests with mocks
|-- docs/
|   `-- API_NOTES.md                  # Comprehensive API technical documentation
|-- assets/
|   `-- screenshots/                  # Application screenshots (.gitkeep preserved)
|-- app.py                            # Streamlit interactive web user interface
|-- translator.py                     # Compatibility shim & CLI entrypoint
|-- requirements.txt                  # Production runtime dependencies
|-- requirements-dev.txt              # Development & test dependencies
|-- setup.py                          # Standard Python package setup
|-- pyproject.toml                    # Modern PEP 518/621 build configuration
|-- run_app.bat                       # 1-Click Streamlit app launcher
|-- run_tests.bat                     # 1-Click test suite runner
|-- push_to_github.bat                # 1-Click GitHub synchronization script
|-- README.md                         # Comprehensive project documentation
`-- .gitignore                        # Git version control ignore rules
```

---

## 5. Prerequisites & Environment Setup

### Prerequisites:
- Python 3.8+ (Tested on Python 3.10)
- `pip` package manager
- Active internet connection (only needed for live translations, not for running unit tests)

### Step 1: Clone the Repository
```bash
git clone https://github.com/asadalikhan8267-acr/CodeAlpha_LanguageTranslationTool.git
cd CodeAlpha_LanguageTranslationTool
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements-dev.txt
```

---

## 6. Execution Instructions

### A. 1-Click Launchers (Windows)
- Double-click **`run_app.bat`** to start the Streamlit web application.
- Double-click **`run_tests.bat`** to run all 26 automated unit tests.
- Double-click **`push_to_github.bat`** to synchronize commits to GitHub.

---

### B. Launching the Web GUI (Streamlit)
```bash
streamlit run app.py
```
Open your web browser at `http://localhost:8501`.

---

### C. Running via Command Line (CLI Mode)
Translate directly in the terminal without opening a browser:

```bash
# Translate English to Urdu (default target)
python translator.py "Hello, welcome to CodeAlpha Internship"

# Translate to another language (e.g., Spanish, French, Arabic)
python translator.py "Artificial Intelligence is transforming the world" --target es
python translator.py "Good morning" --target fr
python translator.py "Peace be upon you" --target ar

# List all supported languages and RTL status
python translator.py --list-languages
```

---

### D. Running the Automated Unit Test Suite
Run the test suite using `pytest`:
```bash
pytest -v
```

Expected output:
```text
============================= test session starts =============================
platform win32 -- Python 3.10.x, pytest-9.x.x
configfile: pyproject.toml
collected 26 items

tests/test_translation.py::TestInputValidation::test_empty_string_raises_validation_error PASSED
tests/test_translation.py::TestInputValidation::test_none_input_raises_validation_error PASSED
tests/test_translation.py::TestInputValidation::test_target_language_cannot_be_autodetect PASSED
tests/test_translation.py::TestInputValidation::test_text_exceeding_max_limit_raises_validation_error PASSED
tests/test_translation.py::TestInputValidation::test_unsupported_source_language_raises_validation_error PASSED
tests/test_translation.py::TestInputValidation::test_unsupported_target_language_raises_validation_error PASSED
tests/test_translation.py::TestInputValidation::test_whitespace_only_raises_validation_error PASSED
tests/test_translation.py::TestIdenticalLanguagesAndRTL::test_identical_source_and_target_skips_network PASSED
tests/test_translation.py::TestIdenticalLanguagesAndRTL::test_identical_urdu_preserves_rtl_flag PASSED
tests/test_translation.py::TestIdenticalLanguagesAndRTL::test_is_rtl_helper PASSED
tests/test_translation.py::TestMockedAPITranslation::test_malformed_json_response_raises_api_response_error PASSED
tests/test_translation.py::TestMockedAPITranslation::test_missing_translated_text_field_raises_api_response_error PASSED
tests/test_translation.py::TestMockedAPITranslation::test_network_connection_error_raises_custom_exception PASSED
tests/test_translation.py::TestMockedAPITranslation::test_rate_limit_429_raises_custom_exception PASSED
tests/test_translation.py::TestMockedAPITranslation::test_request_timeout_raises_custom_exception PASSED
tests/test_translation.py::TestMockedAPITranslation::test_server_500_error_raises_api_response_error PASSED
tests/test_translation.py::TestMockedAPITranslation::test_successful_english_to_urdu_translation PASSED
tests/test_translation.py::TestMockedAPITranslation::test_unescapes_html_entities_in_translated_text PASSED
tests/test_translation.py::TestChunkingAndLongText::test_long_multisentence_text_splits_cleanly PASSED
tests/test_translation.py::TestChunkingAndLongText::test_multichunk_translation_assembles_correctly PASSED
tests/test_translation.py::TestChunkingAndLongText::test_short_text_stays_single_chunk PASSED
tests/test_translation.py::TestPackageAndCLI::test_cli_list_languages PASSED
tests/test_translation.py::TestPackageAndCLI::test_cli_missing_text_returns_error PASSED
tests/test_translation.py::TestPackageAndCLI::test_cli_translate_success PASSED
tests/test_translation.py::TestPackageAndCLI::test_package_exports_exist PASSED
tests/test_translation.py::TestPackageAndCLI::test_root_translator_shim_has_all_symbols PASSED

============================= 26 passed in 0.51s ==============================
```

---

## 7. How to Use the Web Application

1. **Select Source Language:** Choose a specific language or leave on `Auto Detect`.
2. **Select Target Language:** Pick the desired translation language (defaults to `Urdu`).
3. **Enter Text:** Type or paste text into the input box (up to 2,500 characters).
4. **Translate:** Click **"Translate Now"** or press `Ctrl+Enter`.
5. **View Results:** The translated output is formatted with proper typography and alignment (Right-to-Left for Urdu, Arabic, Persian; Left-to-Right for English, Spanish, etc.).
6. **Copy Translation:** Expand the **"Copy Translated Text"** container to easily copy output.
7. **Swap Languages:** Click **"Swap Languages"** to invert source and target choices.
8. **Optional Email:** Enter an email address in the sidebar to increase your free daily quota from 5,000 to 50,000 characters.

---

## 8. Translation API & Limits

- **Endpoint:** `https://api.mymemory.translated.net/get`
- **Protocol:** Public HTTPS GET API.
- **Quota:** 5,000 chars/day anonymous, 50,000 chars/day with registered email address.
- **Chunking:** Sentences exceeding 450 characters are automatically split along punctuation boundaries and reassembled.
- For complete technical specifications, see [`docs/API_NOTES.md`](docs/API_NOTES.md).

---

## 9. Error Handling & Edge Cases

| Condition | Internal Handling | User Feedback |
| :--- | :--- | :--- |
| **Empty or whitespace input** | `ValidationError` raised before calling API | Warning message asking for text input |
| **Identical languages** | Network bypass shortcut | Instant return with "Source & Target are Identical" badge |
| **No internet / DNS failure** | `NetworkError` caught | Alert: "Unable to reach translation server" |
| **Slow connection / Timeout** | `RequestTimeoutError` caught | Alert: "Translation request timed out" |
| **Quota limit (HTTP 429)** | `RateLimitError` caught | Alert: "Daily translation quota exhausted" |
| **Long text (>450 chars)** | Sentence chunker | Seamless piecewise translation and assembly |

---

## 10. Submission Information

- **Internship:** CodeAlpha Artificial Intelligence Internship
- **Task:** Task 1 - Language Translation Tool
- **Submission Archive:** `CodeAlpha_LanguageTranslationTool_Submission.zip`
- **GitHub Repository:** [https://github.com/asadalikhan8267-acr/CodeAlpha_LanguageTranslationTool](https://github.com/asadalikhan8267-acr/CodeAlpha_LanguageTranslationTool)
