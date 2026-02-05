"""Data models for semantic network analysis."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SemanticNode:
    """A node in the semantic network representing a text element."""
    
    id: str
    text: str
    sentence_index: int
    position: int  # Position within sentence
    
    def __hash__(self) -> int:
        """Make SemanticNode hashable for use in sets and dicts."""
        return hash(self.id)
