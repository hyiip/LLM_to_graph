"""Level 2: Config-based prompt generation.

This script demonstrates how to use YAML configuration files
to customize prompt generation without code changes.

Example:
    >>> from use_rag import load_config, get_graph_config, generate_graph_prompt
    >>> config = load_config("example_settings.yaml")
    >>> graph_cfg = get_graph_config(config)
    >>> prompt = generate_graph_prompt(text, entity_types=graph_cfg["entity_types"])

Usage:
    uv run python level2_config.py
    uv run python level2_config.py --config example_settings.yaml
    uv run python level2_config.py --export my_settings.yaml
"""

import argparse
import json
import sys
from pathlib import Path

from use_rag import (
    load_config,
    get_llm_config,
    get_graph_config,
    get_claims_config,
    export_default_settings,
    generate_graph_prompt,
    generate_claims_prompt,
)

DEFAULT_CONFIG_FILE = "default_settings.yaml"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Config-based prompt generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Show default config
  %(prog)s --config example_settings.yaml  # Load and show config
  %(prog)s --export my_settings.yaml    # Export default settings to file
        """,
    )
    parser.add_argument(
        "--config", "-c",
        default=DEFAULT_CONFIG_FILE,
        help=f"Path to YAML config file (default: {DEFAULT_CONFIG_FILE})",
    )
    parser.add_argument(
        "--export", "-e",
        default=None,
        metavar="FILE",
        help="Export default settings to a YAML file",
    )
    return parser.parse_args()


def generate_graph_prompt_from_config(text: str, config_path: str | None = None) -> str:
    """Generate a graph extraction prompt using configuration.

    Args:
        text: The input text to extract entities and relationships from.
        config_path: Path to the YAML configuration file.

    Returns:
        A complete prompt string ready to paste into ChatGPT/Claude.
    """
    config = load_config(config_path)
    graph_cfg = get_graph_config(config)
    return generate_graph_prompt(text, entity_types=graph_cfg["entity_types"])


def generate_claims_prompt_from_config(
    text: str,
    config_path: str | None = None,
    entity_specs: str | None = None,
) -> str:
    """Generate a claims extraction prompt using configuration.

    Args:
        text: The input text to extract claims from.
        config_path: Path to the YAML configuration file.
        entity_specs: Entity specification - overrides config if provided.

    Returns:
        A complete prompt string ready to paste into ChatGPT/Claude.
    """
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
    args = parse_args()

    # Handle export
    if args.export:
        output_path = export_default_settings(args.export)
        print(f"Exported default settings to: {output_path}")
        sys.exit(0)

    sample_text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in
    Cupertino, California in 1976. The company revolutionized the personal
    computer industry.
    """

    print("=" * 60)
    print("LEVEL 2: CONFIG-BASED PROMPT GENERATION")
    print("=" * 60)

    # Auto-generate config file if it doesn't exist
    config_path = args.config
    if not Path(config_path).exists():
        print(f"\nCreating {config_path}...")
        export_default_settings(config_path)

    # Load and show config
    print(f"\n[1] CONFIG FILE: {config_path}")
    print("-" * 40)
    try:
        config = load_config(config_path)
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

        print(f"\n[5] GRAPH PROMPT (from {config_path}):")
        print("-" * 40)
        prompt = generate_graph_prompt_from_config(sample_text, config_path)
        print(prompt[:500] + "...")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
