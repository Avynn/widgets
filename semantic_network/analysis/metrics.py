"""Dialectical metrics computation for semantic network analysis."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from collections import defaultdict


@dataclass
class DialecticalMetrics:
    """Metrics computed from dialectical role analysis.
    
    Attributes:
        transition_matrix: Role-to-role transition counts in text order
        density_per_sentence: Proportion of non-OTHER roles for each sentence
        total_nodes: Total number of nodes analyzed
        role_counts: Count of nodes per dialectical role
    """
    transition_matrix: Dict[Tuple[str, str], int] = field(default_factory=dict)
    density_per_sentence: List[float] = field(default_factory=list)
    total_nodes: int = 0
    role_counts: Dict[str, int] = field(default_factory=dict)


class MetricsCalculator:
    """Calculator for computing dialectical analysis metrics."""
    
    def calculate(self, nodes: List[Dict[str, Any]]) -> DialecticalMetrics:
        """Calculate dialectical metrics from nodes with assigned roles.
        
        Args:
            nodes: List of node dictionaries, each containing:
                - 'role': Dialectical role (e.g., 'THESIS', 'ANTITHESIS', 'SYNTHESIS', 'OTHER')
                - 'sentence_id': Sentence identifier for the node
        
        Returns:
            DialecticalMetrics object with computed metrics
        
        Raises:
            ValueError: If nodes lack required fields
        """
        if not nodes:
            return DialecticalMetrics()
        
        # Validate nodes have required fields
        for node in nodes:
            if 'role' not in node:
                raise ValueError("All nodes must have a 'role' field")
            if 'sentence_id' not in node:
                raise ValueError("All nodes must have a 'sentence_id' field")
        
        metrics = DialecticalMetrics()
        metrics.total_nodes = len(nodes)
        metrics.role_counts = self._calculate_role_counts(nodes)
        metrics.transition_matrix = self._calculate_transition_matrix(nodes)
        metrics.density_per_sentence = self._calculate_density_per_sentence(nodes)
        
        return metrics
    
    def _calculate_role_counts(self, nodes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count occurrences of each dialectical role."""
        role_counts = defaultdict(int)
        for node in nodes:
            role_counts[node['role']] += 1
        return dict(role_counts)
    
    def _calculate_transition_matrix(self, nodes: List[Dict[str, Any]]) -> Dict[Tuple[str, str], int]:
        """Calculate transition matrix tracking role-to-role transitions in text order."""
        transition_matrix = defaultdict(int)
        for i in range(len(nodes) - 1):
            from_role = nodes[i]['role']
            to_role = nodes[i + 1]['role']
            transition_matrix[(from_role, to_role)] += 1
        return dict(transition_matrix)
    
    def _calculate_density_per_sentence(self, nodes: List[Dict[str, Any]]) -> List[float]:
        """Calculate density metric per sentence (proportion of non-OTHER roles)."""
        # Group nodes by sentence
        sentences = defaultdict(list)
        for node in nodes:
            sentences[node['sentence_id']].append(node)
        
        # Calculate density for each sentence
        density_per_sentence = []
        for sentence_id in sorted(sentences.keys()):
            sentence_nodes = sentences[sentence_id]
            total = len(sentence_nodes)
            non_other = sum(1 for node in sentence_nodes if node['role'] != 'OTHER')
            density = non_other / total if total > 0 else 0.0
            density_per_sentence.append(density)
        
        return density_per_sentence
