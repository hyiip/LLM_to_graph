"""Level 1: Manual prompt generation for copy-paste to ChatGPT/Claude.

This module provides functions to generate prompts that can be manually
copied into an LLM interface.

Usage:
    1. Edit TEXT_FILE below to point to your text file
    2. Run: uv run python level1_manual.py
    3. Copy the generated prompt to ChatGPT/Claude
"""

from pathlib import Path

from use_rag import (
    generate_graph_prompt,
    generate_claims_prompt
)

# ============================================================
# USER CONFIGURATION - Edit these values
# ============================================================
TEXT_FILE = "text/01.txt"  # Path to input text file
# ============================================================


if __name__ == "__main__":
    # Load text from file
    text_path = Path(TEXT_FILE)
    if not text_path.exists():
        print(f"Error: Text file not found: {TEXT_FILE}")
        print("\nPlease create the file or update TEXT_FILE in this script.")
        exit(1)

    sample_text = text_path.read_text(encoding="utf-8")
    print(f"Loaded text from: {TEXT_FILE} ({len(sample_text)} chars)")

    print("\n" + "=" * 60)
    print("GRAPH EXTRACTION PROMPT")
    print("=" * 60)
    print(generate_graph_prompt(sample_text))

    print("\n" + "=" * 60)
    print("CLAIMS EXTRACTION PROMPT")
    print("=" * 60)
    print(generate_claims_prompt(sample_text))
