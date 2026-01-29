"""Prompt templates for use_rag package."""

from use_rag.prompts.extract_graph_prompt import (
    GRAPH_EXTRACTION_PROMPT,
    CONTINUE_PROMPT as GRAPH_CONTINUE_PROMPT,
    LOOP_PROMPT as GRAPH_LOOP_PROMPT,
)
from use_rag.prompts.extract_claims_prompt import (
    EXTRACT_CLAIMS_PROMPT,
    CONTINUE_PROMPT as CLAIMS_CONTINUE_PROMPT,
    LOOP_PROMPT as CLAIMS_LOOP_PROMPT,
)

__all__ = [
    "GRAPH_EXTRACTION_PROMPT",
    "GRAPH_CONTINUE_PROMPT",
    "GRAPH_LOOP_PROMPT",
    "EXTRACT_CLAIMS_PROMPT",
    "CLAIMS_CONTINUE_PROMPT",
    "CLAIMS_LOOP_PROMPT",
]
