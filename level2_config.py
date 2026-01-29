"""Level 2: Config-based prompt generation.

This module provides functions to generate prompts based on a YAML configuration
file, allowing customization without code changes.

Example:
    >>> from use_rag.level2_config import generate_graph_prompt_from_config
    >>> prompt = generate_graph_prompt_from_config(
    ...     "Apple Inc. was founded by Steve Jobs...",
    ...     config_path="settings.yaml"
    ... )
"""

from pathlib import Path
from typing import Any

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from use_rag.utils.generate_prompt import (
    generate_graph_prompt,
    generate_claims_prompt,
    DEFAULT_ENTITY_TYPES,
    DEFAULT_CLAIM_DESCRIPTION,
)

# Default LLM settings
DEFAULT_MODEL = "gpt-5.2"
DEFAULT_MAX_GLEANINGS = 1


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.
            If None, returns default configuration.

    Returns:
        Dictionary containing configuration values.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        yaml.YAMLError: If the config file is invalid YAML.
    """
    if config_path is None:
        return get_default_config()

    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required for config file loading. "
            "Install with: pip install pyyaml"
        )

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config or {}


def get_default_config() -> dict[str, Any]:
    """Get default configuration values.

    Returns:
        Dictionary with default configuration.
    """
    return {
        "llm": {
            "model": DEFAULT_MODEL,
        },
        "extract_graph": {
            "entity_types": DEFAULT_ENTITY_TYPES,
            "max_gleanings": DEFAULT_MAX_GLEANINGS,
        },
        "extract_claims": {
            "enabled": True,
            "entity_specs": ", ".join(DEFAULT_ENTITY_TYPES),
            "description": DEFAULT_CLAIM_DESCRIPTION,
            "max_gleanings": DEFAULT_MAX_GLEANINGS,
        },
        "parsing": {
            "record_delimiter": "##",
            "tuple_delimiter": "<|>",
            "completion_marker": "<|COMPLETE|>",
        },
    }


def get_llm_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract LLM configuration from config dict.

    Args:
        config: The full configuration dictionary.

    Returns:
        Dictionary with LLM settings (model, api_key).
    """
    defaults = get_default_config()["llm"]
    llm_config = config.get("llm", {})
    return {
        "model": llm_config.get("model", defaults["model"]),
        "api_key": llm_config.get("api_key"),
    }


def get_graph_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract graph extraction configuration from config dict.

    Args:
        config: The full configuration dictionary.

    Returns:
        Dictionary with graph extraction settings.
    """
    defaults = get_default_config()["extract_graph"]
    graph_config = config.get("extract_graph", {})
    return {
        "entity_types": graph_config.get("entity_types", defaults["entity_types"]),
        "max_gleanings": graph_config.get("max_gleanings", defaults["max_gleanings"]),
    }


def get_claims_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract claims extraction configuration from config dict.

    Args:
        config: The full configuration dictionary.

    Returns:
        Dictionary with claims extraction settings.
    """
    defaults = get_default_config()["extract_claims"]
    claims_config = config.get("extract_claims", {})

    # For entity_specs, also check extract_graph if not specified
    entity_specs = claims_config.get("entity_specs")
    if entity_specs is None:
        graph_config = config.get("extract_graph", {})
        entity_types = graph_config.get("entity_types", DEFAULT_ENTITY_TYPES)
        entity_specs = ", ".join(entity_types)

    return {
        "enabled": claims_config.get("enabled", defaults["enabled"]),
        "entity_specs": entity_specs,
        "description": claims_config.get("description", defaults["description"]),
        "max_gleanings": claims_config.get("max_gleanings", defaults["max_gleanings"]),
    }


def generate_graph_prompt_from_config(
    text: str,
    config_path: str | Path | None = None,
) -> str:
    """Generate a graph extraction prompt using configuration.

    Args:
        text: The input text to extract entities and relationships from.
        config_path: Path to the YAML configuration file.
            If None, uses default configuration.

    Returns:
        A complete prompt string ready to paste into ChatGPT/Claude.

    Example:
        >>> prompt = generate_graph_prompt_from_config(
        ...     "Apple Inc. was founded by Steve Jobs...",
        ...     config_path="settings.yaml"
        ... )
    """
    config = load_config(config_path)
    graph_config = get_graph_config(config)

    return generate_graph_prompt(text, entity_types=graph_config["entity_types"])


def generate_claims_prompt_from_config(
    text: str,
    config_path: str | Path | None = None,
    entity_specs: str | None = None,
) -> str:
    """Generate a claims extraction prompt using configuration.

    Args:
        text: The input text to extract claims from.
        config_path: Path to the YAML configuration file.
            If None, uses default configuration.
        entity_specs: Entity specification - overrides config if provided.

    Returns:
        A complete prompt string ready to paste into ChatGPT/Claude.

    Example:
        >>> prompt = generate_claims_prompt_from_config(
        ...     "Company A was fined for fraud...",
        ...     config_path="settings.yaml"
        ... )
    """
    config = load_config(config_path)
    claims_config = get_claims_config(config)

    # Override with parameter if provided
    if entity_specs is None:
        entity_specs = claims_config["entity_specs"]

    return generate_claims_prompt(
        text,
        entity_specs=entity_specs,
        claim_description=claims_config["description"],
    )


def create_extractors_from_config(config_path: str | Path | None = None):
    """Create LLMClient and extractors from configuration.

    This is a convenience function that creates all
    components from a single config file.

    Args:
        config_path: Path to the YAML configuration file.
            If None, uses default configuration.

    Returns:
        Tuple of (LLMClient, GraphExtractor, ClaimExtractor).

    Raises:
        ImportError: If litellm or openai is not installed.

    Example:
        >>> client, graph_ext, claim_ext = create_extractors_from_config("settings.yaml")
        >>> entities, rels = graph_ext.extract("Apple was founded by Steve Jobs.")
    """
    from use_rag import LLMClient, GraphExtractor, ClaimExtractor

    config = load_config(config_path)

    # Create LLM client
    llm_config = get_llm_config(config)
    client = LLMClient(
        model=llm_config["model"],
        api_key=llm_config["api_key"],
    )

    # Create graph extractor
    graph_config = get_graph_config(config)
    graph_extractor = GraphExtractor(
        client=client,
        entity_types=graph_config["entity_types"],
        max_gleanings=graph_config["max_gleanings"],
    )

    # Create claim extractor
    claims_config = get_claims_config(config)
    claim_extractor = ClaimExtractor(
        client=client,
        entity_specs=claims_config["entity_specs"],
        claim_description=claims_config["description"],
        max_gleanings=claims_config["max_gleanings"],
    )

    return client, graph_extractor, claim_extractor


if __name__ == "__main__":
    # Demo usage with default config
    sample_text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in
    Cupertino, California in 1976. The company revolutionized the personal
    computer industry.
    """

    print("=" * 60)
    print("DEFAULT CONFIG")
    print("=" * 60)
    import json
    print(json.dumps(get_default_config(), indent=2))

    print("\n" + "=" * 60)
    print("GRAPH PROMPT (default config)")
    print("=" * 60)
    print(generate_graph_prompt_from_config(sample_text)[:500] + "...")
