"""Level 4: Automated extraction with LLM client.

This script demonstrates fully automated entity, relationship,
and claim extraction using an LLM API.

Supports multiple LLM providers:
- OpenAI: gpt-5.2 (set OPENAI_API_KEY)
- Anthropic: claude-sonnet-4-5 claude-haiku-4-5 claude-opus-4-5 (set ANTHROPIC_API_KEY)
- Google: gemini/gemini-3-flash-preview gemini/gemini-3-pro-preview (set GEMINI_API_KEY)

Example:
    >>> from use_rag import LLMClient, GraphExtractor
    >>> client = LLMClient(model="gemini/gemini-3-flash-preview")
    >>> extractor = GraphExtractor(client)
    >>> entities, relationships = extractor.extract("Apple Inc. was founded by Steve Jobs...")

Usage:
    uv run python level4_automated.py                    # Uses default model
    uv run python level4_automated.py --model gpt-5.2
    uv run python level4_automated.py --config example_settings.yaml
    uv run python level4_automated.py --config example_settings.yaml --model claude-sonnet-4-5
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

from pathlib import Path

from use_rag import (
    LLMClient,
    GraphExtractor,
    ClaimExtractor,
    load_config,
    get_llm_config,
    get_graph_config,
    get_claims_config,
    export_default_settings,
    PROVIDER_CONFIG,
    detect_provider,
)

DEFAULT_CONFIG_FILE = "default_settings.yaml"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Automated graph extraction using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported providers and models:
  OpenAI:    gpt-5.2                        (requires OPENAI_API_KEY)
  Anthropic: claude-sonnet-4-5, claude-haiku-4-5, claude-opus-4-5
                                            (requires ANTHROPIC_API_KEY)
  Google:    gemini/gemini-3-flash-preview, gemini/gemini-3-pro-preview
                                            (requires GEMINI_API_KEY)

Examples:
  %(prog)s --model gpt-5.2
  %(prog)s --config example_settings.yaml
  %(prog)s --config example_settings.yaml --model claude-sonnet-4-5
        """,
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="Model to use (overrides config file)",
    )
    parser.add_argument(
        "--config", "-c",
        default=DEFAULT_CONFIG_FILE,
        help=f"Path to YAML config file (default: {DEFAULT_CONFIG_FILE})",
    )
    parser.add_argument(
        "--claims",
        action="store_true",
        default=None,
        help="Also extract claims (default: from config or False)",
    )
    return parser.parse_args()


def get_settings(args):
    """Get settings from config file and CLI args (CLI takes precedence)."""
    # Auto-generate config file if it doesn't exist
    config_path = args.config
    if not Path(config_path).exists():
        print(f"Creating {config_path}...")
        export_default_settings(config_path)

    # Load config
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)

    llm_cfg = get_llm_config(config)
    graph_cfg = get_graph_config(config)
    claims_cfg = get_claims_config(config)

    settings = {
        "model": llm_cfg["model"],
        "entity_types": graph_cfg["entity_types"],
        "max_gleanings": graph_cfg["max_gleanings"],
        "extract_claims": claims_cfg["enabled"],
        "claim_entity_specs": claims_cfg["entity_specs"],
        "claim_description": claims_cfg["description"],
        "claim_max_gleanings": claims_cfg["max_gleanings"],
    }

    # CLI args override config
    if args.model:
        settings["model"] = args.model
    if args.claims is not None:
        settings["extract_claims"] = args.claims

    return settings


if __name__ == "__main__":
    args = parse_args()
    settings = get_settings(args)

    sample_text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in
    Cupertino, California in 1976. The company revolutionized the personal
    computer industry with the Macintosh and later transformed the mobile
    phone market with the iPhone in 2007. Steve Jobs passed away in 2011.
    """

    print("=" * 60)
    print("LEVEL 4: AUTOMATED EXTRACTION DEMO")
    print("=" * 60)
    print(f"Config: {args.config}")

    # Check for API key based on detected provider
    model = settings["model"]
    provider = detect_provider(model)
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
        print(f"\nThen run: uv run python level4_automated.py --model {model}")
        sys.exit(0)

    print(f"\nInitializing LLM client with model: {model}")
    if provider:
        print(f"Detected provider: {provider}")
    client = LLMClient(model=model)

    # Graph extraction
    print(f"\nExtracting graph (entity_types={settings['entity_types']}, max_gleanings={settings['max_gleanings']})...")
    graph_extractor = GraphExtractor(
        client,
        entity_types=settings["entity_types"],
        max_gleanings=settings["max_gleanings"],
    )
    entities, relationships = graph_extractor.extract(sample_text)

    print("\nEntities:")
    for e in entities:
        print(f"  - {e.name} ({e.type}): {e.description[:50]}..." if len(e.description) > 50 else f"  - {e.name} ({e.type}): {e.description}")

    print("\nRelationships:")
    for r in relationships:
        print(f"  - {r.source} -> {r.target} (weight={r.weight})")

    # Claims extraction (if enabled)
    if settings["extract_claims"]:
        print("\nExtracting claims...")
        claim_extractor = ClaimExtractor(
            client,
            entity_specs=settings["claim_entity_specs"],
            claim_description=settings["claim_description"],
            max_gleanings=settings.get("claim_max_gleanings", 1),
        )
        claims = claim_extractor.extract(sample_text)

        print("\nClaims:")
        for c in claims:
            status_icon = "✓" if c.status == "TRUE" else "?" if c.status == "SUSPECTED" else "✗"
            print(f"  [{status_icon}] {c.subject}: {c.description[:60]}..." if len(c.description) > 60 else f"  [{status_icon}] {c.subject}: {c.description}")
