"""
translator.py - Backwards-Compatible Entrypoint & CLI Wrapper
--------------------------------------------------------------
Exposes the core translation engine from the `language_translation_tool` package.
Allows direct execution as a script, interactive CLI tool, or backwards-compatible
module import.
"""

import sys
from language_translation_tool.translator import *
from language_translation_tool.translator import main

if __name__ == "__main__":
    sys.exit(main())
