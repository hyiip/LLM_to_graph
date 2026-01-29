"""Level 1: Manual prompt generation for copy-paste to ChatGPT/Claude.

This module provides functions to generate prompts that can be manually
copied into an LLM interface.

Example:
    >>> from use_rag.level1_manual import generate_graph_prompt
    >>> prompt = generate_graph_prompt("Apple Inc. was founded by Steve Jobs...")
    >>> print(prompt)  # Copy this to ChatGPT/Claude
"""

from use_rag import (
    generate_graph_prompt,
    generate_claims_prompt
)




if __name__ == "__main__":
    # Demo usage
    sample_text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in
    Cupertino, California in 1976. The company revolutionized the personal
    computer industry and later transformed the mobile phone market with the
    iPhone in 2007.
    """

    print("=" * 60)
    print("GRAPH EXTRACTION PROMPT")
    print("=" * 60)
    print(generate_graph_prompt(sample_text))
    print()
    print("=" * 60)
    print("CLAIMS EXTRACTION PROMPT")
    print("=" * 60)
    print(generate_claims_prompt(sample_text))
