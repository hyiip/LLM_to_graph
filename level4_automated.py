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

import csv
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
TEXT_FILE = "text/01.txt"     # Path to input text file
OUTPUT_DIR = "output/01/"         # Directory for CSV output files
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


def export_entities_csv(entities, output_path: Path):
    """Export entities to CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "type", "description"])
        for e in entities:
            writer.writerow([e.name, e.type, e.description])


def export_relationships_csv(relationships, output_path: Path):
    """Export relationships to CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "description", "weight"])
        for r in relationships:
            writer.writerow([r.source, r.target, r.description, r.weight])


def export_claims_csv(claims, output_path: Path):
    """Export claims to CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["subject", "object", "type", "status", "start_date", "end_date", "description", "source_text"])
        for c in claims:
            writer.writerow([c.subject, c.object, c.type, c.status, c.start_date, c.end_date, c.description, c.source_text])


if __name__ == "__main__":
    settings = get_settings()

    # Load text from file
    text_path = Path(TEXT_FILE)
    if not text_path.exists():
        print(f"Error: Text file not found: {TEXT_FILE}")
        print("\nPlease create the file or update TEXT_FILE in this script.")
        exit(1)

    sample_text = text_path.read_text(encoding="utf-8")
    print(f"Loaded text from: {TEXT_FILE} ({len(sample_text)} chars)")

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
        desc = e.description[:50]
        print(f"  - {e.name} ({e.type}): {desc}")

    print("\nRelationships:")
    for r in relationships:
        desc = r.description
        print(f"  - {r.source} -> {r.target}: {desc} (weight={r.weight})")

    # Claims extraction (if enabled)
    claims = []
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
            desc = c.description
            print(f"  [{status_icon}] {c.subject}: {desc}")

    # Export to CSV
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True, parents=True)

    entities_file = output_dir / "entities.csv"
    relationships_file = output_dir / "relationships.csv"
    claims_file = output_dir / "claims.csv"

    export_entities_csv(entities, entities_file)
    export_relationships_csv(relationships, relationships_file)
    if claims:
        export_claims_csv(claims, claims_file)

    print(f"\nExported to {OUTPUT_DIR}/:")
    print(f"  - entities.csv ({len(entities)} entities)")
    print(f"  - relationships.csv ({len(relationships)} relationships)")
    if claims:
        print(f"  - claims.csv ({len(claims)} claims)")
