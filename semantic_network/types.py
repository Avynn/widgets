"""Type definitions for semantic network analysis."""

from enum import Enum


class DialecticalRole(Enum):
    """Roles in dialectical analysis."""
    
    THESIS = "thesis"
    ANTITHESIS = "antithesis"
    SYNTHESIS = "synthesis"
    OTHER = "other"
