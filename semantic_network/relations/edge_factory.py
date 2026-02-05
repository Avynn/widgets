"""Factory for creating semantic edges with proper types and metadata."""

from enum import Enum
from typing import Dict, Any, Optional


class EdgeType(Enum):
    """Types of semantic edges in the network."""
    TEMPORAL = "temporal"
    CAUSE = "cause"
    PURPOSE = "purpose"
    CONCESSION = "concession"
    ELABORATION = "elaboration"
    COREFERENCE = "coreference"


class Edge:
    """Represents a directed edge in the semantic network."""
    
    def __init__(self, source: str, target: str, edge_type: EdgeType, metadata: Optional[Dict[str, Any]] = None):
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.metadata = metadata or {}
    
    def __eq__(self, other):
        """Compare edges by source, target, and type (metadata excluded)."""
        if not isinstance(other, Edge):
            return False
        return (self.source == other.source and 
                self.target == other.target and 
                self.edge_type == other.edge_type)
    
    def __hash__(self):
        return hash((self.source, self.target, self.edge_type))
    
    def __repr__(self):
        return f"Edge({self.source} -> {self.target}, {self.edge_type.value})"


def create_temporal_edge(before_node: str, after_node: str, metadata: Optional[Dict[str, Any]] = None) -> Edge:
    """Create temporal edge with correct direction: before_node -> after_node."""
    return Edge(before_node, after_node, EdgeType.TEMPORAL, metadata)


def create_coref_edge(antecedent: str, anaphor: str, source: str = "neural", metadata: Optional[Dict[str, Any]] = None) -> Edge:
    """Create coreference edge with correct direction: antecedent -> anaphor."""
    meta = metadata or {}
    meta["source"] = source
    return Edge(antecedent, anaphor, EdgeType.COREFERENCE, meta)

