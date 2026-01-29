"""Relationship data model."""

from dataclasses import dataclass


@dataclass
class Relationship:
    """Represents a relationship between two entities."""

    source: str
    target: str
    description: str
    weight: float = 1.0

    def __repr__(self) -> str:
        return f"Relationship(source={self.source!r}, target={self.target!r}, weight={self.weight})"
