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
    
    def calculate(self, nodes: List[SemanticNode]) -> DialecticalMetrics:
        """Compute all metrics from nodes with assigned roles.
        
        Args:
            nodes: List of semantic nodes with assigned dialectical roles
            
        Returns:
            DialecticalMetrics containing all computed metrics
        """
        role_counts = self._calculate_role_counts(nodes)
        role_proportions = self._calculate_role_proportions(role_counts, len(nodes))
        transition_matrix = self._calculate_transition_matrix(nodes)
        density_by_sentence = self._calculate_density_by_sentence(nodes)
        
        return DialecticalMetrics(
            role_counts=role_counts,
            role_proportions=role_proportions,
            transition_matrix=transition_matrix,
            density_by_sentence=density_by_sentence
        )
    
    def _calculate_role_counts(self, nodes: List[SemanticNode]) -> Dict[DialecticalRole, int]:
        """Count occurrences of each dialectical role.
        
        Args:
            nodes: List of semantic nodes
            
        Returns:
            Dictionary mapping each role to its count
        """
        counts = {role: 0 for role in DialecticalRole}
        for node in nodes:
            counts[node.role] += 1
        return counts
    
    def _calculate_role_proportions(
        self, 
        role_counts: Dict[DialecticalRole, int], 
        total: int
    ) -> Dict[DialecticalRole, float]:
        """Calculate proportion of each role.
        
        Args:
            role_counts: Dictionary of role counts
            total: Total number of nodes
            
        Returns:
            Dictionary mapping each role to its proportion
        """
        if total == 0:
            return {role: 0.0 for role in DialecticalRole}
        return {role: count / total for role, count in role_counts.items()}
    
    def _calculate_transition_matrix(
        self, 
        nodes: List[SemanticNode]
    ) -> Dict[DialecticalRole, Dict[DialecticalRole, int]]:
        """Calculate role-to-role transition matrix.
        
        Tracks transitions in text order (by position within each sentence,
        then by sentence order).
        
        Args:
            nodes: List of semantic nodes
            
        Returns:
            Nested dictionary mapping from_role -> to_role -> count
        """
        # Initialize matrix
        matrix = {
            role: {target: 0 for target in DialecticalRole}
            for role in DialecticalRole
        }
        
        if len(nodes) < 2:
            return matrix
        
        # Sort nodes by sentence_id and position to get text order
        sorted_nodes = sorted(nodes, key=lambda n: (n.sentence_id, n.position))
        
        # Count transitions
        for i in range(len(sorted_nodes) - 1):
            from_role = sorted_nodes[i].role
            to_role = sorted_nodes[i + 1].role
            matrix[from_role][to_role] += 1
        
        return matrix
    
    def _calculate_density_by_sentence(
        self, 
        nodes: List[SemanticNode]
    ) -> Dict[int, float]:
        """Calculate density of non-OTHER roles per sentence.
        
        Density is the proportion of nodes with non-OTHER roles in each sentence.
        
        Args:
            nodes: List of semantic nodes
            
        Returns:
            Dictionary mapping sentence_id to density value
        """
        # Group nodes by sentence
        sentence_nodes: Dict[int, List[SemanticNode]] = {}
        for node in nodes:
            if node.sentence_id not in sentence_nodes:
                sentence_nodes[node.sentence_id] = []
            sentence_nodes[node.sentence_id].append(node)
        
        # Calculate density for each sentence
        density = {}
        for sentence_id, sent_nodes in sentence_nodes.items():
            total = len(sent_nodes)
            non_other = sum(1 for node in sent_nodes if node.role != DialecticalRole.OTHER)
            density[sentence_id] = non_other / total if total > 0 else 0.0
        
        return density
