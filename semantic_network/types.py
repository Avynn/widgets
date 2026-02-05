"""Core types for semantic network analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DialecticalRole(Enum):
    """Roles in dialectical analysis."""
    THESIS = "thesis"
    ANTITHESIS = "antithesis"
    SYNTHESIS = "synthesis"
    OTHER = "other"


@dataclass
class SemanticNode:
    """A node in the semantic network representing a text unit."""
    text: str
    sentence_index: int
    role: Optional[DialecticalRole] = None
    node_id: Optional[int] = None
