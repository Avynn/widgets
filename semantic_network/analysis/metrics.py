"""Analysis metrics for dialectical role assignments."""

from dataclasses import dataclass
from typing import Dict, List
from semantic_network.types import DialecticalRole, SemanticNode


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
        """Compute all metrics from nodes with assigned roles."""
        role_counts = self._count_roles(nodes)
        return DialecticalMetrics(
            role_counts=role_counts,
            role_proportions=self._compute_proportions(role_counts),
            transition_matrix=self._build_transition_matrix(nodes),
            density_by_sentence=self._compute_density(nodes)
        )
    
    def _count_roles(self, nodes: List[SemanticNode]) -> Dict[DialecticalRole, int]:
        """Count occurrences of each role."""
        counts = {role: 0 for role in DialecticalRole}
        for node in nodes:
            if node.role is not None:
                counts[node.role] += 1
        return counts
    
    def _compute_proportions(self, counts: Dict[DialecticalRole, int]) -> Dict[DialecticalRole, float]:
        """Compute proportion of each role."""
        total = sum(counts.values())
        if total == 0:
            return {role: 0.0 for role in DialecticalRole}
        return {role: count / total for role, count in counts.items()}
    
    def _build_transition_matrix(self, nodes: List[SemanticNode]) -> Dict[DialecticalRole, Dict[DialecticalRole, int]]:
        """Build role transition matrix based on adjacency in text."""
        matrix = {role: {inner_role: 0 for inner_role in DialecticalRole} for role in DialecticalRole}
        for i in range(len(nodes) - 1):
            current_node = nodes[i]
            next_node = nodes[i + 1]
            if current_node.role is not None and next_node.role is not None:
                matrix[current_node.role][next_node.role] += 1
        return matrix
    
    def _compute_density(self, nodes: List[SemanticNode]) -> Dict[int, float]:
        """Compute dialectical density per sentence (proportion of nodes with non-OTHER roles)."""
        sentence_nodes: Dict[int, List[SemanticNode]] = {}
        for node in nodes:
            if node.sentence_index not in sentence_nodes:
                sentence_nodes[node.sentence_index] = []
            sentence_nodes[node.sentence_index].append(node)
        
        density = {}
        for sentence_idx, sent_nodes in sentence_nodes.items():
            total_nodes = len(sent_nodes)
            non_other_nodes = sum(1 for node in sent_nodes if node.role is not None and node.role != DialecticalRole.OTHER)
            density[sentence_idx] = non_other_nodes / total_nodes if total_nodes > 0 else 0.0
        return density
