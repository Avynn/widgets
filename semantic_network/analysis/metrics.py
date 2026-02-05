"""Dialectical analysis metrics computation."""

from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict


@dataclass
class DialecticalMetrics:
    """Metrics computed from dialectical analysis.
    
    Attributes:
        transition_matrix: Role-to-role transitions as (from_role, to_role) -> count.
        density_per_sentence: Proportion of non-OTHER roles per sentence.
        total_nodes: Total number of nodes analyzed.
        role_counts: Count of nodes for each role type.
        average_density: Average density across all sentences.
    """
    transition_matrix: Dict[tuple, int] = field(default_factory=dict)
    density_per_sentence: List[float] = field(default_factory=list)
    total_nodes: int = 0
    role_counts: Dict[str, int] = field(default_factory=dict)
    average_density: float = 0.0


class MetricsCalculator:
    """Calculator for dialectical analysis metrics."""
    
    def calculate(self, nodes: List[Dict]) -> DialecticalMetrics:
        """Calculate metrics from nodes with assigned dialectical roles.
        
        Args:
            nodes: List of node dicts with 'role' and 'sentence_id' attributes.
        
        Returns:
            DialecticalMetrics object with computed metrics.
        """
        if not nodes:
            return DialecticalMetrics()
        
        metrics = DialecticalMetrics()
        metrics.total_nodes = len(nodes)
        metrics.role_counts = self._calculate_role_counts(nodes)
        metrics.transition_matrix = self._calculate_transitions(nodes)
        metrics.density_per_sentence = self._calculate_density(nodes)
        
        if metrics.density_per_sentence:
            metrics.average_density = sum(metrics.density_per_sentence) / len(metrics.density_per_sentence)
        
        return metrics
    
    def _calculate_role_counts(self, nodes: List[Dict]) -> Dict[str, int]:
        """Calculate the count of each role type."""
        role_counts = defaultdict(int)
        for node in nodes:
            role_counts[node.get('role', 'OTHER')] += 1
        return dict(role_counts)
    
    def _calculate_transitions(self, nodes: List[Dict]) -> Dict[tuple, int]:
        """Calculate role-to-role transitions in text order."""
        transitions = defaultdict(int)
        for i in range(len(nodes) - 1):
            from_role = nodes[i].get('role', 'OTHER')
            to_role = nodes[i + 1].get('role', 'OTHER')
            transitions[(from_role, to_role)] += 1
        return dict(transitions)
    
    def _calculate_density(self, nodes: List[Dict]) -> List[float]:
        """Calculate density of non-OTHER roles per sentence."""
        sentences = defaultdict(list)
        for node in nodes:
            sentences[node.get('sentence_id', 0)].append(node)
        
        densities = []
        for sentence_id in sorted(sentences.keys()):
            sentence_nodes = sentences[sentence_id]
            if not sentence_nodes:
                densities.append(0.0)
                continue
            non_other_count = sum(1 for node in sentence_nodes 
                                 if node.get('role', 'OTHER') != 'OTHER')
            densities.append(non_other_count / len(sentence_nodes))
        return densities
