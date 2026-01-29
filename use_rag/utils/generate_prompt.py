from use_rag.prompts.extract_graph_prompt import GRAPH_EXTRACTION_PROMPT
from use_rag.prompts.extract_claims_prompt import EXTRACT_CLAIMS_PROMPT

# Default entity types from GraphRAG
DEFAULT_ENTITY_TYPES = ["organization", "person", "geo", "event"]

# Default claim description
DEFAULT_CLAIM_DESCRIPTION = (
    "Any claims or facts that could be relevant to information discovery."
)

def generate_graph_prompt(
    text: str,
    entity_types: list[str] | None = None,
) -> str:
    """Generate a graph extraction prompt for manual use.

    Args:
        text: The input text to extract entities and relationships from.
        entity_types: List of entity types to extract. Defaults to
            ["organization", "person", "geo", "event"].

    Returns:
        A complete prompt string ready to paste into ChatGPT/Claude.

    Example:
        >>> prompt = generate_graph_prompt(
        ...     "Apple Inc. was founded by Steve Jobs in 1976.",
        ...     entity_types=["organization", "person"]
        ... )
        >>> print(prompt)
    """
    if entity_types is None:
        entity_types = DEFAULT_ENTITY_TYPES

    # Format entity types as comma-separated uppercase string
    entity_types_str = ",".join(t.upper() for t in entity_types)

    return GRAPH_EXTRACTION_PROMPT.format(
        entity_types=entity_types_str,
        input_text=text,
    )


def generate_claims_prompt(
    text: str,
    entity_specs: str | None = None,
    claim_description: str | None = None,
) -> str:
    """Generate a claims extraction prompt for manual use.

    Args:
        text: The input text to extract claims from.
        entity_specs: Entity specification - can be entity types (e.g., "organization")
            or specific entity names (e.g., "Company A, Person B").
            Defaults to "organization, person, geo, event".
        claim_description: Description of the types of claims to extract.
            Defaults to "Any claims or facts that could be relevant to
            information discovery."

    Returns:
        A complete prompt string ready to paste into ChatGPT/Claude.

    Example:
        >>> prompt = generate_claims_prompt(
        ...     "Company A was fined for fraud in 2022.",
        ...     entity_specs="organization",
        ...     claim_description="red flags associated with an entity"
        ... )
        >>> print(prompt)
    """
    if entity_specs is None:
        entity_specs = ", ".join(DEFAULT_ENTITY_TYPES)

    if claim_description is None:
        claim_description = DEFAULT_CLAIM_DESCRIPTION

    return EXTRACT_CLAIMS_PROMPT.format(
        entity_specs=entity_specs,
        claim_description=claim_description,
        input_text=text,
    )