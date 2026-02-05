"""Tests for dialectical metrics calculation."""

import pytest

from semantic_network.types import DialecticalRole
from semantic_network.models import SemanticNode
from semantic_network.analysis.metrics import DialecticalMetrics, MetricsCalculator


class TestMetricsCalculator:
    """Tests for MetricsCalculator class."""
    
    def test_calculate_with_empty_list(self):
        """Should handle empty node list."""
        calculator = MetricsCalculator()
        metrics = calculator.calculate([])
        
        assert all(count == 0 for count in metrics.role_counts.values())
        assert all(prop == 0.0 for prop in metrics.role_proportions.values())
        assert metrics.density_by_sentence == {}
    
    def test_calculate_role_counts(self):
        """Should count each role correctly."""
        nodes = [
            SemanticNode("text1", DialecticalRole.THESIS, 0, 0),
            SemanticNode("text2", DialecticalRole.THESIS, 0, 1),
            SemanticNode("text3", DialecticalRole.ANTITHESIS, 1, 0),
            SemanticNode("text4", DialecticalRole.SYNTHESIS, 1, 1),
            SemanticNode("text5", DialecticalRole.OTHER, 2, 0),
        ]
        
        calculator = MetricsCalculator()
        metrics = calculator.calculate(nodes)
        
        assert metrics.role_counts[DialecticalRole.THESIS] == 2
        assert metrics.role_counts[DialecticalRole.ANTITHESIS] == 1
        assert metrics.role_counts[DialecticalRole.SYNTHESIS] == 1
        assert metrics.role_counts[DialecticalRole.OTHER] == 1
    
    def test_calculate_role_proportions(self):
        """Should calculate proportions correctly."""
        nodes = [
            SemanticNode("text1", DialecticalRole.THESIS, 0, 0),
            SemanticNode("text2", DialecticalRole.THESIS, 0, 1),
            SemanticNode("text3", DialecticalRole.ANTITHESIS, 1, 0),
            SemanticNode("text4", DialecticalRole.OTHER, 1, 1),
        ]
        
        calculator = MetricsCalculator()
        metrics = calculator.calculate(nodes)
        
        assert metrics.role_proportions[DialecticalRole.THESIS] == 0.5
        assert metrics.role_proportions[DialecticalRole.ANTITHESIS] == 0.25
        assert metrics.role_proportions[DialecticalRole.SYNTHESIS] == 0.0
        assert metrics.role_proportions[DialecticalRole.OTHER] == 0.25
    
    def test_transition_matrix(self):
        """Should track role transitions in text order."""
        nodes = [
            SemanticNode("text1", DialecticalRole.THESIS, 0, 0),
            SemanticNode("text2", DialecticalRole.ANTITHESIS, 0, 1),
            SemanticNode("text3", DialecticalRole.SYNTHESIS, 1, 0),
            SemanticNode("text4", DialecticalRole.THESIS, 1, 1),
        ]
        
        calculator = MetricsCalculator()
        metrics = calculator.calculate(nodes)
        
        # Check specific transitions
        assert metrics.transition_matrix[DialecticalRole.THESIS][DialecticalRole.ANTITHESIS] == 1
        assert metrics.transition_matrix[DialecticalRole.ANTITHESIS][DialecticalRole.SYNTHESIS] == 1
        assert metrics.transition_matrix[DialecticalRole.SYNTHESIS][DialecticalRole.THESIS] == 1
    
    def test_density_by_sentence(self):
        """Should calculate density as proportion of non-OTHER roles per sentence."""
        nodes = [
            SemanticNode("text1", DialecticalRole.THESIS, 0, 0),
            SemanticNode("text2", DialecticalRole.ANTITHESIS, 0, 1),
            SemanticNode("text3", DialecticalRole.OTHER, 0, 2),
            SemanticNode("text4", DialecticalRole.OTHER, 0, 3),
            SemanticNode("text5", DialecticalRole.SYNTHESIS, 1, 0),
            SemanticNode("text6", DialecticalRole.OTHER, 1, 1),
        ]
        
        calculator = MetricsCalculator()
        metrics = calculator.calculate(nodes)
        
        # Sentence 0: 2 non-OTHER out of 4 = 0.5
        assert metrics.density_by_sentence[0] == 0.5
        # Sentence 1: 1 non-OTHER out of 2 = 0.5
        assert metrics.density_by_sentence[1] == 0.5
    
    def test_density_all_other(self):
        """Should handle sentence with all OTHER roles."""
        nodes = [
            SemanticNode("text1", DialecticalRole.OTHER, 0, 0),
            SemanticNode("text2", DialecticalRole.OTHER, 0, 1),
        ]
        
        calculator = MetricsCalculator()
        metrics = calculator.calculate(nodes)
        
        assert metrics.density_by_sentence[0] == 0.0
    
    def test_density_all_non_other(self):
        """Should handle sentence with no OTHER roles."""
        nodes = [
            SemanticNode("text1", DialecticalRole.THESIS, 0, 0),
            SemanticNode("text2", DialecticalRole.ANTITHESIS, 0, 1),
        ]
        
        calculator = MetricsCalculator()
        metrics = calculator.calculate(nodes)
        
        assert metrics.density_by_sentence[0] == 1.0
