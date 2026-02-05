"""Data models for semantic network analysis."""

from dataclasses import dataclass
from typing import Optional

from semantic_network.types import DialecticalRole


@dataclass
class SemanticNode:
    """A semantic node with dialectical role assignment."""
    
    text: str
    role: DialecticalRole
    sentence_id: int
    position: int
    node_id: Optional[int] = None
