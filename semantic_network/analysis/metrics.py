"""Analysis metrics for dialectical analysis."""

from dataclasses import dataclass
from typing import Dict, List
from semantic_network.types import DialecticalRole
from semantic_network.models import SemanticNode


@dataclass
class DialecticalMetrics:
    """Metrics computed from dialectical role assignments."""
    
    role_counts: Dict[DialecticalRole, int]
    role_proportions: Dict[DialecticalRole, float]
    transition_matrix: Dict[DialecticalRole, Dict[DialecticalRole, int]]
    density_by_sentence: Dict[int, float]


class MetricsCalculator:
    """Calculate dialectical metrics from role assignments."""
    
    def calculate(
        self,
        role_assignments: Dict[str, DialecticalRole],
        nodes: List[SemanticNode]
    ) -> DialecticalMetrics:
        """Compute all metrics from role assignments.
        
        Args:
            role_assignments: Mapping of node IDs to their dialectical roles
            nodes: List of semantic nodes in the network
            
        Returns:
            DialecticalMetrics containing all computed metrics
        """
        counts = self._count_roles(role_assignments)
        proportions = self._compute_proportions(counts)
        transition_matrix = self._build_transition_matrix(role_assignments, nodes)
        density = self._compute_density(role_assignments, nodes)
        
        return DialecticalMetrics(
            role_counts=counts,
            role_proportions=proportions,
            transition_matrix=transition_matrix,
            density_by_sentence=density
        )
    
    def _count_roles(
        self,
        assignments: Dict[str, DialecticalRole]
    ) -> Dict[DialecticalRole, int]:
        """Count occurrences of each role.
        
        Args:
            assignments: Mapping of node IDs to their dialectical roles
            
        Returns:
            Dictionary mapping each role to its count
        """
        counts = {role: 0 for role in DialecticalRole}
        for role in assignments.values():
            counts[role] += 1
        return counts
    
    def _compute_proportions(
        self,
        counts: Dict[DialecticalRole, int]
    ) -> Dict[DialecticalRole, float]:
        """Compute proportion of each role.
        
        Args:
            counts: Dictionary mapping roles to their counts
            
        Returns:
            Dictionary mapping each role to its proportion (0.0 to 1.0)
        """
        total = sum(counts.values())
        if total == 0:
            return {role: 0.0 for role in DialecticalRole}
        return {role: count / total for role, count in counts.items()}
    
    def _build_transition_matrix(
        self,
        assignments: Dict[str, DialecticalRole],
        nodes: List[SemanticNode]
    ) -> Dict[DialecticalRole, Dict[DialecticalRole, int]]:
        """Build role transition matrix based on adjacency in text.
        
        The transition matrix tracks how often one role is followed by another
        in the sequential order of nodes in the text.
        
        Args:
            assignments: Mapping of node IDs to their dialectical roles
            nodes: List of semantic nodes in sequential order
            
        Returns:
            Nested dictionary where matrix[role_a][role_b] = count of
            transitions from role_a to role_b
        """
        # Initialize matrix with all role combinations
        matrix = {
            role: {other_role: 0 for other_role in DialecticalRole}
            for role in DialecticalRole
        }
        
        # Sort nodes by sentence index and position to ensure text order
        sorted_nodes = sorted(nodes, key=lambda n: (n.sentence_index, n.position))
        
        # Count transitions between adjacent nodes
        for i in range(len(sorted_nodes) - 1):
            current_node = sorted_nodes[i]
            next_node = sorted_nodes[i + 1]
            
            current_role = assignments.get(current_node.id, DialecticalRole.UNASSIGNED)
            next_role = assignments.get(next_node.id, DialecticalRole.UNASSIGNED)
            
            matrix[current_role][next_role] += 1
        
        return matrix
    
    def _compute_density(
        self,
        assignments: Dict[str, DialecticalRole],
        nodes: List[SemanticNode]
    ) -> Dict[int, float]:
        """Compute dialectical density per sentence.
        
        Density is the proportion of nodes with non-UNASSIGNED roles
        within each sentence.
        
        Args:
            assignments: Mapping of node IDs to their dialectical roles
            nodes: List of semantic nodes
            
        Returns:
            Dictionary mapping sentence indices to their dialectical density
        """
        # Group nodes by sentence
        sentences: Dict[int, List[SemanticNode]] = {}
        for node in nodes:
            if node.sentence_index not in sentences:
                sentences[node.sentence_index] = []
            sentences[node.sentence_index].append(node)
        
        # Calculate density for each sentence
        density = {}
        for sentence_idx, sentence_nodes in sentences.items():
            total_nodes = len(sentence_nodes)
            if total_nodes == 0:
                density[sentence_idx] = 0.0
                continue
            
            assigned_nodes = sum(
                1 for node in sentence_nodes
                if assignments.get(node.id, DialecticalRole.UNASSIGNED) != DialecticalRole.UNASSIGNED
            )
            
            density[sentence_idx] = assigned_nodes / total_nodes
        
        return density
