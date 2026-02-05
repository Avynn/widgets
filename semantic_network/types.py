"""Type definitions for semantic network analysis."""

from enum import Enum


class DialecticalRole(Enum):
    """Dialectical roles that can be assigned to semantic nodes."""
    
    THESIS = "thesis"
    ANTITHESIS = "antithesis"
    SYNTHESIS = "synthesis"
    UNASSIGNED = "unassigned"
