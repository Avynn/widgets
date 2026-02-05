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
        """
        Create a semantic edge.
        
        Args:
            source: Source node identifier
            target: Target node identifier
            edge_type: Type of the edge
            metadata: Additional edge metadata
        """
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.metadata = metadata or {}
    
    def __eq__(self, other):
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
    """
    Create a temporal edge with correct direction.
    
    For "X before Y": edge goes X -> Y
    For "X after Y": edge goes Y -> X (reversed at call site)
    
    Args:
        before_node: Node that happens first
        after_node: Node that happens after
        metadata: Additional metadata
        
    Returns:
        Edge from before_node to after_node
    """
    return Edge(before_node, after_node, EdgeType.TEMPORAL, metadata)


def create_coref_edge(antecedent: str, anaphor: str, source: str = "neural", metadata: Optional[Dict[str, Any]] = None) -> Edge:
    """
    Create a coreference edge with correct direction.
    
    Edge direction: antecedent -> anaphor (linguistic convention)
    
    Args:
        antecedent: The referring expression that comes first
        anaphor: The expression that refers back
        source: Resolution source ("neural" or "heuristic")
        metadata: Additional metadata
        
    Returns:
        Edge from antecedent to anaphor
    """
    meta = metadata or {}
    meta["source"] = source
    return Edge(antecedent, anaphor, EdgeType.COREFERENCE, meta)
