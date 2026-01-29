"""Level 4: Automated extraction with LLM client.

This script demonstrates fully automated entity, relationship,
and claim extraction using an LLM API.

Supports multiple LLM providers:
- OpenAI: gpt-4, gpt-4.1 (set OPENAI_API_KEY)
- Anthropic: claude-3-opus-20240229, claude-3-sonnet-20240229 (set ANTHROPIC_API_KEY)
- Google: gemini/gemini-pro (set GEMINI_API_KEY)

Example:
    >>> from use_rag import LLMClient, GraphExtractor
    >>> client = LLMClient(model="gpt-4.1")
    >>> extractor = GraphExtractor(client)
    >>> entities, relationships = extractor.extract("Apple Inc. was founded by Steve Jobs...")

Usage:
    uv run python level4_automated.py                    # Uses default (gpt-4.1)
    uv run python level4_automated.py --model gpt-4.1
    uv run python level4_automated.py --model claude-3-opus-20240229
    uv run python level4_automated.py --model gemini/gemini-pro
"""

import argparse
import os
import sys

# Load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use environment variables directly

from use_rag import LLMClient, GraphExtractor
from use_rag.client import PROVIDER_CONFIG, detect_provider


def parse_args():
    parser = argparse.ArgumentParser(
        description="Automated graph extraction using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported providers and models:
  OpenAI:    gpt-4, gpt-4.1, o1-*, o3-*     (requires OPENAI_API_KEY)
  Anthropic: claude-3-opus-*, claude-3-*    (requires ANTHROPIC_API_KEY)
  Google:    gemini/gemini-pro, gemini-*    (requires GEMINI_API_KEY)

Examples:
  %(prog)s --model gpt-4.1
  %(prog)s --model claude-3-opus-20240229
  %(prog)s --model gemini/gemini-pro
        """,
    )
    parser.add_argument(
        "--model", "-m",
        default="gpt-4.1",
        help="Model to use (default: gpt-4.1)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    sample_text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in
    Cupertino, California in 1976. The company revolutionized the personal
    computer industry with the Macintosh and later transformed the mobile
    phone market with the iPhone in 2007. Steve Jobs passed away in 2011.
    """

    print("=" * 60)
    print("LEVEL 4: AUTOMATED EXTRACTION DEMO")
    print("=" * 60)

    # Check for API key based on detected provider
    provider = detect_provider(args.model)
    if provider and provider in PROVIDER_CONFIG:
        env_var = PROVIDER_CONFIG[provider]["env_var"]
        api_key = os.environ.get(env_var)
    else:
        # Fallback: check all provider env vars
        api_key = None
        env_var = "API key"
        for cfg in PROVIDER_CONFIG.values():
            api_key = os.environ.get(cfg["env_var"])
            if api_key:
                break

    if not api_key:
        print(f"\nNote: Set {env_var} environment variable to run live demo.")
        print("\nSupported providers:")
        print("  OpenAI:    export OPENAI_API_KEY='your-key'")
        print("  Anthropic: export ANTHROPIC_API_KEY='your-key'")
        print("  Google:    export GEMINI_API_KEY='your-key'")
        print(f"\nThen run: uv run python level4_automated.py --model {args.model}")
        sys.exit(0)

    print(f"\nInitializing LLM client with model: {args.model}")
    if provider:
        print(f"Detected provider: {provider}")
    client = LLMClient(model=args.model)

    print("\nExtracting graph from sample text (with gleaning)...")
    graph_extractor = GraphExtractor(client, max_gleanings=1)
    entities, relationships = graph_extractor.extract(sample_text)

    print("\nEntities:")
    for e in entities:
        print(f"  - {e.name} ({e.type})")

    print("\nRelationships:")
    for r in relationships:
        print(f"  - {r.source} -> {r.target} (weight={r.weight})")
