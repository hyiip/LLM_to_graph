"""Level 2: Config-based prompt generation.

This script demonstrates how to use YAML configuration files
to customize prompt generation without code changes.

Usage:
    1. Edit CONFIG and EXPORT below
    2. Run: uv run python level2_config.py
"""

from pathlib import Path

from use_rag import (
    DEFAULT_CONFIG_FILE,
    load_config,
    get_llm_config,
    get_graph_config,
    get_claims_config,
    export_default_settings,
    generate_graph_prompt,
    generate_claims_prompt,
)

# ============================================================
# USER CONFIGURATION - Edit these values
# ============================================================
CONFIG = DEFAULT_CONFIG_FILE  # Path to config file (auto-created if not exists)
# ============================================================


def generate_graph_prompt_from_config(text: str, config_path: str | None = None) -> str:
    """Generate a graph extraction prompt using configuration."""
    config = load_config(config_path)
    graph_cfg = get_graph_config(config)
    return generate_graph_prompt(text, entity_types=graph_cfg["entity_types"])


def generate_claims_prompt_from_config(
    text: str,
    config_path: str | None = None,
    entity_specs: str | None = None,
) -> str:
    """Generate a claims extraction prompt using configuration."""
    config = load_config(config_path)
    claims_cfg = get_claims_config(config)

    if entity_specs is None:
        entity_specs = claims_cfg["entity_specs"]

    return generate_claims_prompt(
        text,
        entity_specs=entity_specs,
        claim_description=claims_cfg["description"],
    )


if __name__ == "__main__":
    import json

    # Auto-generate config file if it doesn't exist
    if not Path(CONFIG).exists():
        print(f"Creating {CONFIG}...")
        export_default_settings(CONFIG)

    sample_text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in
    Cupertino, California in 1976. The company revolutionized the personal
    computer industry.
    """

    print("=" * 60)
    print("LEVEL 2: CONFIG-BASED PROMPT GENERATION")
    print("=" * 60)

    print(f"\n[1] CONFIG FILE: {CONFIG}")
    print("-" * 40)
    config = load_config(CONFIG)
    print(json.dumps(config, indent=2, default=str))

    print("\n[2] LLM CONFIG:")
    print("-" * 40)
    print(json.dumps(get_llm_config(config), indent=2))

    print("\n[3] GRAPH CONFIG:")
    print("-" * 40)
    print(json.dumps(get_graph_config(config), indent=2))

    print("\n[4] CLAIMS CONFIG:")
    print("-" * 40)
    print(json.dumps(get_claims_config(config), indent=2))

    print(f"\n[5] GRAPH PROMPT (from {CONFIG}):")
    print("-" * 40)
    prompt = generate_graph_prompt_from_config(sample_text, CONFIG)
    print(prompt[:500] + "...")
