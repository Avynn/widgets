"""Data models for semantic network analysis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticNode:
    """A node in the semantic network representing a text element."""
    
    id: str
    text: str
    sentence_index: int
    position: int  # Position within sentence
