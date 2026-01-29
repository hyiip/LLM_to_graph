"""use_rag - A minimal GraphRAG workaround for LLM-to-graph extraction.

This package provides reusable modules for extracting entities,
relationships, and claims from text using LLMs.

Example:
    >>> from use_rag.utils.generate_prompt import generate_graph_prompt
    >>> prompt = generate_graph_prompt("Apple Inc. was founded by Steve Jobs...")
    >>> print(prompt)  # Copy to ChatGPT
"""

# Models
from use_rag.models import Entity, Relationship, Claim

# Utils
from use_rag.utils.generate_prompt import (
    generate_graph_prompt,
    generate_claims_prompt,
    DEFAULT_ENTITY_TYPES,
    DEFAULT_CLAIM_DESCRIPTION,
)

# Parser
from use_rag.parser import (
    parse_graph_output,
    parse_claims_output,
    RECORD_DELIMITER,
    TUPLE_DELIMITER,
    COMPLETION_MARKER,
)

# Client
from use_rag.client import LLMClient, PROVIDER_CONFIG, detect_provider

# Extractors
from use_rag.extractors import GraphExtractor, ClaimExtractor

# Configs
from use_rag.configs import (
    load_config,
    get_default_config,
    get_llm_config,
    get_graph_config,
    get_claims_config,
    export_default_settings,
    create_extractors_from_config,
)

# Prompts (for advanced usage)
from use_rag.prompts import (
    GRAPH_EXTRACTION_PROMPT,
    GRAPH_CONTINUE_PROMPT,
    GRAPH_LOOP_PROMPT,
    EXTRACT_CLAIMS_PROMPT,
    CLAIMS_CONTINUE_PROMPT,
    CLAIMS_LOOP_PROMPT,
)

__version__ = "0.1.0"

__all__ = [
    # Models
    "Entity",
    "Relationship",
    "Claim",
    # Utils
    "generate_graph_prompt",
    "generate_claims_prompt",
    "DEFAULT_ENTITY_TYPES",
    "DEFAULT_CLAIM_DESCRIPTION",
    # Parser
    "parse_graph_output",
    "parse_claims_output",
    "RECORD_DELIMITER",
    "TUPLE_DELIMITER",
    "COMPLETION_MARKER",
    # Client
    "LLMClient",
    "PROVIDER_CONFIG",
    "detect_provider",
    # Extractors
    "GraphExtractor",
    "ClaimExtractor",
    # Configs
    "load_config",
    "get_default_config",
    "get_llm_config",
    "get_graph_config",
    "get_claims_config",
    "export_default_settings",
    "create_extractors_from_config",
    # Prompts
    "GRAPH_EXTRACTION_PROMPT",
    "GRAPH_CONTINUE_PROMPT",
    "GRAPH_LOOP_PROMPT",
    "EXTRACT_CLAIMS_PROMPT",
    "CLAIMS_CONTINUE_PROMPT",
    "CLAIMS_LOOP_PROMPT",
]
