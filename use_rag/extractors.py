"""Extractor classes for automated graph and claim extraction.

This module provides classes for fully automated entity, relationship,
and claim extraction using an LLM API.
"""

from typing import Tuple

from use_rag.client import LLMClient
from use_rag.models import Entity, Relationship, Claim
from use_rag.parser import parse_graph_output, parse_claims_output
from use_rag.utils.generate_prompt import (
    generate_graph_prompt,
    generate_claims_prompt,
    DEFAULT_ENTITY_TYPES,
    DEFAULT_CLAIM_DESCRIPTION,
)
from use_rag.prompts.extract_graph_prompt import (
    CONTINUE_PROMPT as GRAPH_CONTINUE_PROMPT,
    LOOP_PROMPT as GRAPH_LOOP_PROMPT,
)
from use_rag.prompts.extract_claims_prompt import (
    CONTINUE_PROMPT as CLAIMS_CONTINUE_PROMPT,
    LOOP_PROMPT as CLAIMS_LOOP_PROMPT,
)


class GraphExtractor:
    """Automated graph extraction from text.

    This class combines prompt generation, LLM calling, and output parsing
    for end-to-end entity and relationship extraction.

    Supports "gleaning" - iteratively asking the LLM to extract more entities
    that may have been missed in the initial extraction.
    """

    def __init__(
        self,
        client: LLMClient,
        entity_types: list[str] | None = None,
        max_gleanings: int = 1,
    ):
        """Initialize the graph extractor.

        Args:
            client: An LLMClient instance for API calls.
            entity_types: List of entity types to extract.
                Defaults to ["organization", "person", "geo", "event"].
            max_gleanings: Maximum number of gleaning iterations to find
                additional entities. Set to 0 to disable gleaning, -1 for
                unlimited gleaning until LLM says no more. Defaults to 1.
        """
        self.client = client
        self.entity_types = entity_types or DEFAULT_ENTITY_TYPES
        self.max_gleanings = max_gleanings

    def extract(self, text: str) -> Tuple[list[Entity], list[Relationship]]:
        """Extract entities and relationships from text.

        Args:
            text: The input text to process.

        Returns:
            A tuple of (entities, relationships) lists.
        """
        prompt = generate_graph_prompt(text, entity_types=self.entity_types)
        messages = [{"role": "user", "content": prompt}]

        response = self.client.chat(messages)
        messages.append({"role": "assistant", "content": response})

        entities, relationships = parse_graph_output(response)

        iteration = 0
        while self.max_gleanings < 0 or iteration < self.max_gleanings:
            iteration += 1

            messages.append({"role": "user", "content": GRAPH_CONTINUE_PROMPT})
            continue_response = self.client.chat(messages)
            messages.append({"role": "assistant", "content": continue_response})

            new_entities, new_relationships = parse_graph_output(continue_response)
            entities.extend(new_entities)
            relationships.extend(new_relationships)

            messages.append({"role": "user", "content": GRAPH_LOOP_PROMPT})
            loop_response = self.client.chat(messages)
            messages.append({"role": "assistant", "content": loop_response})

            if loop_response.strip().upper().startswith("N"):
                break

        # Deduplicate entities by name
        seen_entities = {}
        for e in entities:
            if e.name not in seen_entities:
                seen_entities[e.name] = e
        entities = list(seen_entities.values())

        # Deduplicate relationships by (source, target)
        seen_rels = {}
        for r in relationships:
            key = (r.source, r.target)
            if key not in seen_rels:
                seen_rels[key] = r
        relationships = list(seen_rels.values())

        return entities, relationships


class ClaimExtractor:
    """Automated claim extraction from text.

    This class combines prompt generation, LLM calling, and output parsing
    for end-to-end claim extraction.

    Supports "gleaning" - iteratively asking the LLM to extract more claims
    that may have been missed in the initial extraction.
    """

    def __init__(
        self,
        client: LLMClient,
        entity_specs: str | None = None,
        claim_description: str | None = None,
        max_gleanings: int = 1,
    ):
        """Initialize the claim extractor.

        Args:
            client: An LLMClient instance for API calls.
            entity_specs: Entity specification for extraction.
                Defaults to "organization, person, geo, event".
            claim_description: Description of claims to extract.
                Defaults to "Any claims or facts that could be relevant
                to information discovery."
            max_gleanings: Maximum number of gleaning iterations to find
                additional claims. Set to 0 to disable gleaning, -1 for
                unlimited gleaning until LLM says no more. Defaults to 1.
        """
        self.client = client
        self.entity_specs = entity_specs or ", ".join(DEFAULT_ENTITY_TYPES)
        self.claim_description = claim_description or DEFAULT_CLAIM_DESCRIPTION
        self.max_gleanings = max_gleanings

    def extract(self, text: str) -> list[Claim]:
        """Extract claims from text.

        Args:
            text: The input text to process.

        Returns:
            A list of Claim objects.
        """
        prompt = generate_claims_prompt(
            text,
            entity_specs=self.entity_specs,
            claim_description=self.claim_description,
        )

        messages = [{"role": "user", "content": prompt}]

        response = self.client.chat(messages)
        messages.append({"role": "assistant", "content": response})

        claims = parse_claims_output(response)

        iteration = 0
        while self.max_gleanings < 0 or iteration < self.max_gleanings:
            iteration += 1

            messages.append({"role": "user", "content": CLAIMS_CONTINUE_PROMPT})
            continue_response = self.client.chat(messages)
            messages.append({"role": "assistant", "content": continue_response})

            new_claims = parse_claims_output(continue_response)
            claims.extend(new_claims)

            messages.append({"role": "user", "content": CLAIMS_LOOP_PROMPT})
            loop_response = self.client.chat(messages)
            messages.append({"role": "assistant", "content": loop_response})

            if loop_response.strip().upper().startswith("N"):
                break

        # Deduplicate claims by (subject, type, description hash)
        seen_claims = {}
        for c in claims:
            key = (c.subject, c.type, hash(c.description[:50]))
            if key not in seen_claims:
                seen_claims[key] = c
        claims = list(seen_claims.values())

        return claims
