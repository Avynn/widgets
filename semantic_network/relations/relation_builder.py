"""Build semantic relations from text with discourse markers."""

from typing import List, Tuple
from .edge_factory import Edge, EdgeType, create_temporal_edge


# Multi-word discourse markers mapping
DISCOURSE_MARKERS = {
    "even though": EdgeType.CONCESSION,
    "in spite of": EdgeType.CONCESSION,
    "as well as": EdgeType.ELABORATION,
    "in order to": EdgeType.PURPOSE,
    "before": EdgeType.TEMPORAL,
    "after": EdgeType.TEMPORAL,
    "because": EdgeType.CAUSE,
}


class RelationBuilder:
    """Builds semantic relations from text."""
    
    def __init__(self):
        self.edges = []
    
    def add_temporal_relation(self, text: str, node1: str, node2: str) -> Edge:
        """Add temporal relation with correct direction for before/after."""
        text_lower = text.lower()
        
        if "before" in text_lower:
            edge = create_temporal_edge(node1, node2)  # X before Y -> X -> Y
        elif "after" in text_lower:
            edge = create_temporal_edge(node2, node1)  # X after Y -> Y -> X
        else:
            edge = create_temporal_edge(node1, node2)
        
        self.edges.append(edge)
        return edge
    
    def detect_discourse_marker(self, text: str) -> Tuple[str, EdgeType]:
        """Detect discourse markers in text, checking multi-word markers first."""
        text_lower = text.lower()
        
        # Check multi-word markers first
        for marker in ["even though", "in spite of", "as well as", "in order to"]:
            if marker in text_lower:
                return (marker, DISCOURSE_MARKERS[marker])
        
        # Check single-word markers
        for marker, edge_type in DISCOURSE_MARKERS.items():
            if len(marker.split()) == 1 and marker in text_lower:
                return (marker, edge_type)
        
        return (None, None)
    
    def build_relation(self, text: str, node1: str, node2: str) -> Edge:
        """Build a semantic relation from text."""
        marker, edge_type = self.detect_discourse_marker(text)
        
        if edge_type == EdgeType.TEMPORAL:
            return self.add_temporal_relation(text, node1, node2)
        elif edge_type:
            edge = Edge(node1, node2, edge_type)
            self.edges.append(edge)
            return edge
        else:
            edge = Edge(node1, node2, EdgeType.ELABORATION)
            self.edges.append(edge)
            return edge
    
    def get_edges(self) -> List[Edge]:
        """Get all built edges."""
        return self.edges

