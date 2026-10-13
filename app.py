"""
app.py - Language Translation Tool (Streamlit Web Interface)
-------------------------------------------------------------
CodeAlpha Artificial Intelligence Internship - Task 1

An interactive, responsive web application for real-time multilingual translation
powered by the MyMemory Translation API. Supports English <-> Urdu with full
Right-to-Left (RTL) script rendering, language auto-detection, and error handling.
"""

import html
import sys
import streamlit as st
try:
    import language_translation_tool.translator as translator
except ImportError:
    import translator

# Configure page layout and metadata
st.set_page_config(
    page_title="Language Translation Tool | CodeAlpha AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern styling, clean badges, and proper Urdu RTL rendering
st.markdown(
    """
    <style>
    /* Main container enhancements */
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    
    /* Translation card containers */
    .output-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        min-height: 180px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Right-to-Left styling for Urdu, Arabic, Persian */
    .rtl-text {
        direction: rtl;
        text-align: right;
        font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Segoe UI', Tahoma, sans-serif;
        font-size: 1.35rem;
        line-height: 2.1;
        color: #0F172A;
    }
    
    /* Left-to-Right styling for English and Latin scripts */
    .ltr-text {
        direction: ltr;
        text-align: left;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #0F172A;
    }

    /* Status badge */
    .metric-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        font-size: 0.82rem;
        font-weight: 600;
        border-radius: 6px;
        background-color: #EEF2FF;
        color: #4338CA;
        margin-right: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------

if "source_text" not in st.session_state:
    st.session_state.source_text = ""
if "translated_result" not in st.session_state:
    st.session_state.translated_result = None
if "source_lang_index" not in st.session_state:
    st.session_state.source_lang_index = 1  # Default: English
if "target_lang_index" not in st.session_state:
    st.session_state.target_lang_index = 1  # Default: Urdu (index in target list)


# Prepare Language Options
# Map human-friendly display label -> ISO code
LANG_CODES = list(translator.SUPPORTED_LANGUAGES.keys())

SOURCE_OPTIONS = [
    f"{data['name']} ({data['native']})" if code != "autodetect" else "🌐 Auto Detect"
    for code, data in translator.SUPPORTED_LANGUAGES.items()
]

# Target cannot be "autodetect"
TARGET_CODES = [code for code in LANG_CODES if code != "autodetect"]
TARGET_OPTIONS = [
    f"{translator.SUPPORTED_LANGUAGES[code]['name']} ({translator.SUPPORTED_LANGUAGES[code]['native']})"
    for code in TARGET_CODES
]

# Find indices for default selection (Source: English, Target: Urdu)
default_src_idx = LANG_CODES.index("en") if "en" in LANG_CODES else 0
default_tgt_idx = TARGET_CODES.index("ur") if "ur" in TARGET_CODES else 0

if "initialized_defaults" not in st.session_state:
    st.session_state.source_lang_select = SOURCE_OPTIONS[default_src_idx]
    st.session_state.target_lang_select = TARGET_OPTIONS[default_tgt_idx]
    st.session_state.initialized_defaults = True


# ---------------------------------------------------------------------------
# Sidebar: Settings & API Information
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚙️ Tool Settings")
    st.markdown("Configure options for the **CodeAlpha Translation Tool**.")

    user_email = st.text_input(
        "Optional Email (Extended Quota):",
        value="",
        placeholder="your_email@domain.com",
        help="Providing an email address raises your free daily quota from 5,000 to 50,000 characters per day on MyMemory API.",
    )

    request_timeout = st.slider(
        "Request Timeout (Seconds):",
        min_value=5,
        max_value=30,
        value=10,
        step=1,
        help="Maximum time to wait for a response from the translation server.",
    )

    st.markdown("---")
    st.subheader("📌 Project Details")
    st.markdown(
        """
        - **Program:** CodeAlpha AI Internship
        - **Task:** 1 — Language Translation Tool
        - **API:** MyMemory (Translated.net)
        - **Engine:** Python 3.10 + Streamlit
        - **Pair Highlight:** English ⇄ Urdu
        """
    )

    st.markdown("---")
    st.subheader("💡 Usage Tips")
    st.markdown(
        """
        - For **Urdu**, type or paste Urdu text directly. The output will automatically format Right-to-Left (RTL).
        - Use **Auto Detect** if you are unsure of the source language.
        - Click **Swap Languages** to flip source and target instantly.
        """
    )


# ---------------------------------------------------------------------------
# Main Header
# ---------------------------------------------------------------------------

st.markdown('<div class="main-title">🌐 Language Translation Tool</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">A clean, real-time AI translation application supporting English, Urdu, and major international languages.</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Language Selector Bar
# ---------------------------------------------------------------------------

col_lang_src, col_swap, col_lang_tgt = st.columns([5, 1, 5])

with col_lang_src:
    selected_src_label = st.selectbox(
        "Source Language:",
        options=SOURCE_OPTIONS,
        key="source_lang_select",
    )

with col_swap:
    st.write("")  # vertical alignment spacer
    st.write("")
    if st.button("⇄", help="Swap Source and Target Languages", use_container_width=True):
        # Swap logic:
        # Determine current source code and target code
        current_src_idx = SOURCE_OPTIONS.index(st.session_state.source_lang_select)
        current_src_code = LANG_CODES[current_src_idx]

        current_tgt_idx = TARGET_OPTIONS.index(st.session_state.target_lang_select)
        current_tgt_code = TARGET_CODES[current_tgt_idx]

        # Cannot set target to autodetect
        new_src_code = current_tgt_code
        new_tgt_code = current_src_code if current_src_code != "autodetect" else "en"

        new_src_idx = LANG_CODES.index(new_src_code)
        new_tgt_idx = TARGET_CODES.index(new_tgt_code)

        st.session_state.source_lang_select = SOURCE_OPTIONS[new_src_idx]
        st.session_state.target_lang_select = TARGET_OPTIONS[new_tgt_idx]
        st.rerun()

with col_lang_tgt:
    selected_tgt_label = st.selectbox(
        "Target Language:",
        options=TARGET_OPTIONS,
        key="target_lang_select",
    )

# Extract actual ISO codes
src_index = SOURCE_OPTIONS.index(selected_src_label)
source_lang_code = LANG_CODES[src_index]

tgt_index = TARGET_OPTIONS.index(selected_tgt_label)
target_lang_code = TARGET_CODES[tgt_index]


# ---------------------------------------------------------------------------
# Translation Interface: Two-Column Layout
# ---------------------------------------------------------------------------

col_input, col_output = st.columns(2)

with col_input:
    st.markdown("### 📝 Original Text")
    
    input_text = st.text_area(
        label="Input text to translate:",
        value=st.session_state.source_text,
        height=220,
        placeholder="Enter text here (e.g. 'Hello, welcome to our AI project!' or 'آپ کا نام کیا ہے؟')...",
        label_visibility="collapsed",
        key="user_text_input",
    )

    # Character Counter & Limits
    char_count = len(input_text)
    limit_color = "#10B981" if char_count <= 500 else ("#F59E0B" if char_count <= translator.MAX_TOTAL_CHARS else "#EF4444")
    st.markdown(
        f"<span style='font-size:0.85rem; color:{limit_color}; font-weight:600;'>"
        f"Character count: {char_count} / {translator.MAX_TOTAL_CHARS} max</span>",
        unsafe_allow_html=True,
    )

    # Action Buttons Row
    btn_col1, btn_col2 = st.columns([3, 2])
    with btn_col1:
        translate_clicked = st.button("🚀 Translate Now", type="primary", use_container_width=True)
    with btn_col2:
        clear_clicked = st.button("🗑️ Clear All", use_container_width=True)


with col_output:
    st.markdown("### 🎯 Translated Result")
    output_placeholder = st.empty()


# ---------------------------------------------------------------------------
# Action Handlers
# ---------------------------------------------------------------------------

# Handle Clear All
if clear_clicked:
    st.session_state.source_text = ""
    st.session_state.translated_result = None
    st.rerun()

# Handle Translation Execution
if translate_clicked:
    if not input_text or not input_text.strip():
        st.warning("⚠️ Please enter some text before clicking Translate.")
        st.session_state.translated_result = None
    else:
        with st.spinner("Translating text via MyMemory API..."):
            try:
                result = translator.translate(
                    text=input_text,
                    source_lang=source_lang_code,
                    target_lang=target_lang_code,
                    email=user_email if user_email else None,
                    timeout=request_timeout,
                )
                st.session_state.translated_result = result
                st.session_state.source_text = input_text
            except translator.ValidationError as exc:
                st.warning(f"⚠️ Input Notice: {exc}")
                st.session_state.translated_result = None
            except translator.RateLimitError as exc:
                st.error("🛑 Daily Quota Reached: The daily free translation quota for this service has been reached. Please try again tomorrow, or provide an email address in the sidebar to extend your quota to 50,000 characters.")
                with st.expander("Show details", expanded=False):
                    st.caption(str(exc))
                st.session_state.translated_result = None
            except translator.RequestTimeoutError as exc:
                st.error("⏳ Request Timeout: The translation server took too long to respond. Please check your internet connection or try again in a moment.")
                with st.expander("Show details", expanded=False):
                    st.caption(str(exc))
                st.session_state.translated_result = None
            except translator.NetworkError as exc:
                st.error("🌐 Connection Issue: Unable to connect to the online translation service. Please verify your internet connection and try again.")
                with st.expander("Show details", expanded=False):
                    st.caption(str(exc))
                st.session_state.translated_result = None
            except translator.APIResponseError as exc:
                st.error("⚠️ Service Notice: The translation service encountered an issue processing this request. Please try again in a few moments.")
                with st.expander("Show details", expanded=False):
                    st.caption(str(exc))
                st.session_state.translated_result = None
            except Exception as exc:
                st.error("❌ Unexpected Error: An unexpected issue occurred while processing your request. Please try again.")
                with st.expander("Show details", expanded=False):
                    st.caption(str(exc))
                st.session_state.translated_result = None


# ---------------------------------------------------------------------------
# Display Translated Output
# ---------------------------------------------------------------------------

res: translator.TranslationResult = st.session_state.translated_result

with output_placeholder.container():
    if res:
        # Determine CSS class based on RTL or LTR
        text_css_class = "rtl-text" if res.is_rtl else "ltr-text"

        # Sanitize HTML output to prevent injection/XSS vulnerabilities while preserving formatting
        safe_translated_text = html.escape(res.translated_text).replace("\n", "<br>")

        st.markdown(
            f"""
            <div class="output-card">
                <div class="{text_css_class}">
                    {safe_translated_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        # Metadata / Badges
        badge_html = ""
        if res.detected_language and source_lang_code == "autodetect":
            badge_html += f"<span class='metric-badge'>Detected Source: {res.detected_language.upper()}</span>"
        if res.is_identical:
            badge_html += "<span class='metric-badge' style='background-color:#FEF3C7; color:#92400E;'>Source & Target are Identical</span>"
        if res.match_score > 0:
            badge_html += f"<span class='metric-badge'>Quality Match: {int(res.match_score * 100)}%</span>"
        if res.chunks_count > 1:
            badge_html += f"<span class='metric-badge'>Processed in {res.chunks_count} Chunks</span>"

        if badge_html:
            st.markdown(badge_html, unsafe_allow_html=True)

        st.write("")
        # Copy to clipboard convenience area
        with st.expander("📋 Copy Translated Text", expanded=False):
            st.text_area(
                label="Copyable text:",
                value=res.translated_text,
                height=100,
                label_visibility="collapsed",
                help="Select all (Ctrl+A) and Copy (Ctrl+C).",
            )
    else:
        st.markdown(
            """
            <div class="output-card" style="display:flex; align-items:center; justify-content:center; color:#94A3B8;">
                <p style="text-align:center; font-style:italic;">Your translation will appear here after clicking "Translate Now".</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 0.85rem; color: #6B7280;">
        CodeAlpha Artificial Intelligence Internship • Task 1: Language Translation Tool • Developed with Python 3.10 & Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
