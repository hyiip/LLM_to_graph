"""Level 4: Automated extraction with LLM client.

This script demonstrates fully automated entity, relationship,
and claim extraction using an LLM API.

Supports multiple LLM providers:
- OpenAI: gpt-5.2 (set OPENAI_API_KEY)
- Anthropic: claude-sonnet-4-5, claude-haiku-4-5, claude-opus-4-5 (set ANTHROPIC_API_KEY)
- Google: gemini/gemini-3-flash-preview, gemini/gemini-3-pro-preview (set GEMINI_API_KEY)

Usage:
    1. Edit CONFIG, MODEL, and EXTRACT_CLAIMS below
    2. Run: uv run python level4_automated.py
"""

import os
import sys
from pathlib import Path

# Load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from use_rag import (
    DEFAULT_CONFIG_FILE,
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

# ============================================================
# USER CONFIGURATION - Edit these values
# ============================================================
CONFIG = DEFAULT_CONFIG_FILE  # Path to config file (auto-created if not exists)
MODEL = None                  # Override model (None = use config file)
EXTRACT_CLAIMS = None         # Override claims extraction (None = use config file)
# ============================================================


def get_settings():
    """Get settings from config file and overrides."""
    # Auto-generate config file if it doesn't exist
    if not Path(CONFIG).exists():
        print(f"Creating {CONFIG}...")
        export_default_settings(CONFIG)

    # Load config
    config = load_config(CONFIG)
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

    # Apply overrides
    if MODEL is not None:
        settings["model"] = MODEL
    if EXTRACT_CLAIMS is not None:
        settings["extract_claims"] = EXTRACT_CLAIMS

    return settings


if __name__ == "__main__":
    settings = get_settings()

    sample_text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in
    Cupertino, California in 1976. The company revolutionized the personal
    computer industry with the Macintosh and later transformed the mobile
    phone market with the iPhone in 2007. Steve Jobs passed away in 2011.
    """

    print("=" * 60)
    print("LEVEL 4: AUTOMATED EXTRACTION DEMO")
    print("=" * 60)
    print(f"Config: {CONFIG}")

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
        print("\nThen run: uv run python level4_automated.py")
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
        desc = e.description[:50] + "..." if len(e.description) > 50 else e.description
        print(f"  - {e.name} ({e.type}): {desc}")

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
            status_icon = "+" if c.status == "TRUE" else "?" if c.status == "SUSPECTED" else "-"
            desc = c.description[:60] + "..." if len(c.description) > 60 else c.description
            print(f"  [{status_icon}] {c.subject}: {desc}")
