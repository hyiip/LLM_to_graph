"""Parser functions for LLM output.

This module provides functions to parse the text output from an LLM
into structured Entity, Relationship, and Claim objects.
"""

import re
from typing import Tuple

from use_rag.models import Entity, Relationship, Claim


def clean_str(text: str) -> str:
    """Clean and normalize a string.

    Args:
        text: The string to clean.

    Returns:
        The cleaned string with normalized whitespace.
    """
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# Delimiters from GraphRAG
RECORD_DELIMITER = "##"
TUPLE_DELIMITER = "<|>"
COMPLETION_MARKER = "<|COMPLETE|>"


def parse_graph_output(llm_output: str) -> Tuple[list[Entity], list[Relationship]]:
    """Parse LLM graph extraction output into Entity and Relationship objects.

    Args:
        llm_output: The raw text output from the LLM.

    Returns:
        A tuple of (entities, relationships) lists.
    """
    entities: list[Entity] = []
    relationships: list[Relationship] = []

    text = llm_output.replace(COMPLETION_MARKER, "").strip()
    records = text.split(RECORD_DELIMITER)

    for record in records:
        record = record.strip()
        if not record:
            continue

        match = re.search(r"\((.+?)\)\s*$", record, re.DOTALL)
        if not match:
            continue

        content = match.group(1)
        parts = content.split(TUPLE_DELIMITER)

        if len(parts) < 2:
            continue

        record_type = clean_str(parts[0]).lower().strip('"\'')

        if record_type == "entity" and len(parts) >= 4:
            entity = Entity(
                name=clean_str(parts[1]),
                type=clean_str(parts[2]),
                description=clean_str(parts[3]),
            )
            entities.append(entity)

        elif record_type == "relationship" and len(parts) >= 4:
            weight = 1.0
            if len(parts) >= 5:
                try:
                    weight = float(clean_str(parts[4]))
                except ValueError:
                    weight = 1.0

            relationship = Relationship(
                source=clean_str(parts[1]),
                target=clean_str(parts[2]),
                description=clean_str(parts[3]),
                weight=weight,
            )
            relationships.append(relationship)

    return entities, relationships


def parse_claims_output(llm_output: str) -> list[Claim]:
    """Parse LLM claims extraction output into Claim objects.

    Args:
        llm_output: The raw text output from the LLM.

    Returns:
        A list of Claim objects.
    """
    claims: list[Claim] = []

    text = llm_output.replace(COMPLETION_MARKER, "").strip()
    records = text.split(RECORD_DELIMITER)

    for record in records:
        record = record.strip()
        if not record:
            continue

        match = re.search(r"\((.+?)\)\s*$", record, re.DOTALL)
        if not match:
            continue

        content = match.group(1)
        parts = content.split(TUPLE_DELIMITER)

        if len(parts) < 8:
            continue

        obj = clean_str(parts[1])
        if obj.upper() == "NONE":
            obj = None

        start_date = clean_str(parts[4])
        if start_date.upper() == "NONE":
            start_date = None

        end_date = clean_str(parts[5])
        if end_date.upper() == "NONE":
            end_date = None

        claim = Claim(
            subject=clean_str(parts[0]),
            object=obj,
            type=clean_str(parts[2]),
            status=clean_str(parts[3]),
            start_date=start_date,
            end_date=end_date,
            description=clean_str(parts[6]),
            source_text=clean_str(parts[7]),
        )
        claims.append(claim)

    return claims
