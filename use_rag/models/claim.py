"""Claim data model."""

from dataclasses import dataclass


@dataclass
class Claim:
    """Represents an extracted claim from text."""

    subject: str
    object: str | None
    type: str
    status: str  # TRUE, FALSE, SUSPECTED
    start_date: str | None
    end_date: str | None
    description: str
    source_text: str

    def __repr__(self) -> str:
        return f"Claim(subject={self.subject!r}, type={self.type!r}, status={self.status!r})"
