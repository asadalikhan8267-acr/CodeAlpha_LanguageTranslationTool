from setuptools import setup, find_packages

setup(
    name="codealpha-language-translation-tool",
    version="1.0.0",
    description="Multilingual Language Translation Tool with Urdu RTL Support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="CodeAlpha AI Intern",
    packages=find_packages(include=["language_translation_tool", "language_translation_tool.*"]),
    install_requires=[
        "streamlit>=1.30.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0"],
    },
    entry_points={
        "console_scripts": [
            "translate-tool=language_translation_tool.translator:main",
        ],
    },
    python_requires=">=3.8",
)
