"""Tests for dialectical metrics calculation."""

import pytest
from semantic_network.types import DialecticalRole, SemanticNode
from semantic_network.analysis.metrics import DialecticalMetrics, MetricsCalculator


class TestMetricsCalculator:
    """Tests for MetricsCalculator class."""
    
    def test_calculate_with_empty_nodes(self):
        """Test metrics calculation with empty node list."""
        calculator = MetricsCalculator()
        metrics = calculator.calculate([])
        
        assert metrics.role_counts == {role: 0 for role in DialecticalRole}
        assert metrics.role_proportions == {role: 0.0 for role in DialecticalRole}
        assert metrics.density_by_sentence == {}
    
    def test_count_roles(self):
        """Test role counting."""
        nodes = [
            SemanticNode("thesis text", 0, DialecticalRole.THESIS),
            SemanticNode("antithesis text", 0, DialecticalRole.ANTITHESIS),
            SemanticNode("thesis text 2", 1, DialecticalRole.THESIS),
            SemanticNode("other text", 1, DialecticalRole.OTHER),
        ]
        calculator = MetricsCalculator()
        counts = calculator._count_roles(nodes)
        
        assert counts[DialecticalRole.THESIS] == 2
        assert counts[DialecticalRole.ANTITHESIS] == 1
        assert counts[DialecticalRole.SYNTHESIS] == 0
        assert counts[DialecticalRole.OTHER] == 1
    
    def test_compute_proportions(self):
        """Test proportion calculation."""
        counts = {
            DialecticalRole.THESIS: 2,
            DialecticalRole.ANTITHESIS: 1,
            DialecticalRole.SYNTHESIS: 1,
            DialecticalRole.OTHER: 0,
        }
        calculator = MetricsCalculator()
        proportions = calculator._compute_proportions(counts)
        
        assert proportions[DialecticalRole.THESIS] == 0.5
        assert proportions[DialecticalRole.ANTITHESIS] == 0.25
        assert proportions[DialecticalRole.SYNTHESIS] == 0.25
        assert proportions[DialecticalRole.OTHER] == 0.0
    
    def test_build_transition_matrix(self):
        """Test transition matrix construction."""
        nodes = [
            SemanticNode("thesis", 0, DialecticalRole.THESIS),
            SemanticNode("antithesis", 0, DialecticalRole.ANTITHESIS),
            SemanticNode("synthesis", 1, DialecticalRole.SYNTHESIS),
            SemanticNode("thesis 2", 1, DialecticalRole.THESIS),
        ]
        calculator = MetricsCalculator()
        matrix = calculator._build_transition_matrix(nodes)
        
        assert matrix[DialecticalRole.THESIS][DialecticalRole.ANTITHESIS] == 1
        assert matrix[DialecticalRole.ANTITHESIS][DialecticalRole.SYNTHESIS] == 1
        assert matrix[DialecticalRole.SYNTHESIS][DialecticalRole.THESIS] == 1
    
    def test_compute_density(self):
        """Test dialectical density calculation."""
        nodes = [
            SemanticNode("thesis", 0, DialecticalRole.THESIS),
            SemanticNode("other", 0, DialecticalRole.OTHER),
            SemanticNode("antithesis", 1, DialecticalRole.ANTITHESIS),
            SemanticNode("synthesis", 1, DialecticalRole.SYNTHESIS),
            SemanticNode("other 2", 1, DialecticalRole.OTHER),
        ]
        calculator = MetricsCalculator()
        density = calculator._compute_density(nodes)
        
        # Sentence 0: 1 non-OTHER out of 2 = 0.5
        assert density[0] == 0.5
        # Sentence 1: 2 non-OTHER out of 3 = 0.666...
        assert abs(density[1] - 2/3) < 0.001
    
    def test_full_calculation(self):
        """Test complete metrics calculation."""
        nodes = [
            SemanticNode("thesis", 0, DialecticalRole.THESIS),
            SemanticNode("antithesis", 0, DialecticalRole.ANTITHESIS),
            SemanticNode("synthesis", 1, DialecticalRole.SYNTHESIS),
        ]
        calculator = MetricsCalculator()
        metrics = calculator.calculate(nodes)
        
        assert isinstance(metrics, DialecticalMetrics)
        assert metrics.role_counts[DialecticalRole.THESIS] == 1
        assert metrics.role_proportions[DialecticalRole.THESIS] == 1/3
        assert metrics.density_by_sentence[0] == 1.0
        assert metrics.density_by_sentence[1] == 1.0
