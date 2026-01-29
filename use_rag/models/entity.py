"""Entity data model."""

from dataclasses import dataclass


@dataclass
class Entity:
    """Represents an extracted entity from text."""

    name: str
    type: str
    description: str

    def __repr__(self) -> str:
        return f"Entity(name={self.name!r}, type={self.type!r})"
