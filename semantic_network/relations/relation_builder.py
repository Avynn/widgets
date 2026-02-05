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
        """
        Add a temporal relation based on discourse marker.
        
        Handles correct edge direction:
        - "X before Y" -> edge from X to Y
        - "X after Y" -> edge from Y to X
        
        Args:
            text: The full text containing the relation
            node1: First node mentioned
            node2: Second node mentioned
            
        Returns:
            The created edge
        """
        text_lower = text.lower()
        
        if "before" in text_lower:
            # "X before Y" means X happens first, so edge X -> Y
            edge = create_temporal_edge(node1, node2)
        elif "after" in text_lower:
            # "X after Y" means Y happens first, so edge Y -> X
            edge = create_temporal_edge(node2, node1)
        else:
            # Default to before semantics
            edge = create_temporal_edge(node1, node2)
        
        self.edges.append(edge)
        return edge
    
    def detect_discourse_marker(self, text: str) -> Tuple[str, EdgeType]:
        """
        Detect discourse markers in text, including multi-word markers.
        
        Multi-word markers are checked first for proper matching.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (marker found, edge type) or (None, None)
        """
        text_lower = text.lower()
        
        # Check multi-word markers first (longest to shortest)
        multi_word_markers = [
            "even though", "in spite of", "as well as", "in order to"
        ]
        
        for marker in multi_word_markers:
            if marker in text_lower:
                return (marker, DISCOURSE_MARKERS[marker])
        
        # Check single-word markers
        for marker, edge_type in DISCOURSE_MARKERS.items():
            if len(marker.split()) == 1 and marker in text_lower:
                return (marker, edge_type)
        
        return (None, None)
    
    def build_relation(self, text: str, node1: str, node2: str) -> Edge:
        """
        Build a semantic relation from text.
        
        Args:
            text: Text containing the relation
            node1: First node
            node2: Second node
            
        Returns:
            Created edge
        """
        marker, edge_type = self.detect_discourse_marker(text)
        
        if edge_type == EdgeType.TEMPORAL:
            return self.add_temporal_relation(text, node1, node2)
        elif edge_type:
            edge = Edge(node1, node2, edge_type)
            self.edges.append(edge)
            return edge
        else:
            # Default relation
            edge = Edge(node1, node2, EdgeType.ELABORATION)
            self.edges.append(edge)
            return edge
    
    def get_edges(self) -> List[Edge]:
        """Get all built edges."""
        return self.edges
