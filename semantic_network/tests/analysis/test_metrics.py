"""Tests for dialectical metrics computation."""

import pytest
from semantic_network.analysis import DialecticalMetrics, MetricsCalculator


class TestDialecticalMetrics:
    """Test cases for DialecticalMetrics dataclass."""
    
    def test_default_initialization(self):
        """Test that DialecticalMetrics initializes with correct defaults."""
        metrics = DialecticalMetrics()
        assert metrics.transition_matrix == {}
        assert metrics.density_per_sentence == []
        assert metrics.total_nodes == 0
        assert metrics.role_counts == {}
        assert metrics.average_density == 0.0


class TestMetricsCalculator:
    """Test cases for MetricsCalculator class."""
    
    def test_calculate_empty_nodes(self):
        """Test calculate with empty node list."""
        calculator = MetricsCalculator()
        metrics = calculator.calculate([])
        assert metrics.total_nodes == 0
        assert metrics.role_counts == {}
    
    def test_calculate_returns_populated_metrics(self):
        """Test that calculate() returns populated DialecticalMetrics."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 0},
            {'role': 'SYNTHESIS', 'sentence_id': 1}
        ]
        metrics = calculator.calculate(nodes)
        
        assert isinstance(metrics, DialecticalMetrics)
        assert metrics.total_nodes == 3
        assert len(metrics.role_counts) > 0
        assert len(metrics.transition_matrix) > 0
        assert len(metrics.density_per_sentence) > 0
    
    def test_transition_matrix_tracks_role_transitions(self):
        """Test that transition matrix tracks role-to-role transitions."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 0},
            {'role': 'THESIS', 'sentence_id': 1},
            {'role': 'SYNTHESIS', 'sentence_id': 1}
        ]
        metrics = calculator.calculate(nodes)
        
        assert metrics.transition_matrix[('THESIS', 'ANTITHESIS')] == 1
        assert metrics.transition_matrix[('ANTITHESIS', 'THESIS')] == 1
        assert metrics.transition_matrix[('THESIS', 'SYNTHESIS')] == 1
    
    def test_density_metric_per_sentence(self):
        """Test that density is proportion of non-OTHER roles per sentence."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'OTHER', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 1},
            {'role': 'SYNTHESIS', 'sentence_id': 1},
        ]
        metrics = calculator.calculate(nodes)
        
        assert len(metrics.density_per_sentence) == 2
        assert metrics.density_per_sentence[0] == 0.5  # 1/2
        assert metrics.density_per_sentence[1] == 1.0  # 2/2
    
    def test_density_all_other_roles(self):
        """Test density when all nodes have OTHER role."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'OTHER', 'sentence_id': 0},
            {'role': 'OTHER', 'sentence_id': 0}
        ]
        metrics = calculator.calculate(nodes)
        assert metrics.density_per_sentence[0] == 0.0
    
    def test_average_density_calculation(self):
        """Test that average density is correctly calculated."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'OTHER', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 1},
            {'role': 'SYNTHESIS', 'sentence_id': 1},
        ]
        metrics = calculator.calculate(nodes)
        assert metrics.average_density == 0.75  # (0.5 + 1.0) / 2
    
    def test_role_counts(self):
        """Test that role counts are correctly calculated."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 1},
            {'role': 'OTHER', 'sentence_id': 1}
        ]
        metrics = calculator.calculate(nodes)
        assert metrics.role_counts['THESIS'] == 2
        assert metrics.role_counts['ANTITHESIS'] == 1
        assert metrics.role_counts['OTHER'] == 1
