"""Tests for dialectical metrics computation."""

import pytest
from semantic_network.analysis.metrics import DialecticalMetrics, MetricsCalculator


class TestDialecticalMetrics:
    """Tests for DialecticalMetrics dataclass."""
    
    def test_default_initialization(self):
        """Should initialize with default empty values."""
        metrics = DialecticalMetrics()
        assert metrics.transition_matrix == {}
        assert metrics.density_per_sentence == []
        assert metrics.total_nodes == 0
        assert metrics.role_counts == {}


class TestMetricsCalculator:
    """Tests for MetricsCalculator class."""
    
    def test_calculate_empty_nodes(self):
        """Should return empty metrics for empty node list."""
        calculator = MetricsCalculator()
        metrics = calculator.calculate([])
        assert metrics.total_nodes == 0
        assert metrics.role_counts == {}
        assert metrics.transition_matrix == {}
        assert metrics.density_per_sentence == []
    
    def test_calculate_missing_role_field(self):
        """Should raise ValueError if nodes lack 'role' field."""
        calculator = MetricsCalculator()
        nodes = [{'sentence_id': 0}]
        with pytest.raises(ValueError, match="must have a 'role' field"):
            calculator.calculate(nodes)
    
    def test_calculate_missing_sentence_id_field(self):
        """Should raise ValueError if nodes lack 'sentence_id' field."""
        calculator = MetricsCalculator()
        nodes = [{'role': 'THESIS'}]
        with pytest.raises(ValueError, match="must have a 'sentence_id' field"):
            calculator.calculate(nodes)
    
    def test_calculate_single_node(self):
        """Should calculate metrics for single node."""
        calculator = MetricsCalculator()
        nodes = [{'role': 'THESIS', 'sentence_id': 0}]
        metrics = calculator.calculate(nodes)
        
        assert metrics.total_nodes == 1
        assert metrics.role_counts == {'THESIS': 1}
        assert metrics.transition_matrix == {}
        assert metrics.density_per_sentence == [1.0]
    
    def test_calculate_role_counts(self):
        """Should correctly count role occurrences."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 0},
            {'role': 'THESIS', 'sentence_id': 1},
            {'role': 'SYNTHESIS', 'sentence_id': 1},
            {'role': 'OTHER', 'sentence_id': 2}
        ]
        metrics = calculator.calculate(nodes)
        
        assert metrics.role_counts == {
            'THESIS': 2, 'ANTITHESIS': 1, 'SYNTHESIS': 1, 'OTHER': 1
        }
    
    def test_calculate_transition_matrix(self):
        """Should track role-to-role transitions in text order."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 0},
            {'role': 'THESIS', 'sentence_id': 1},
            {'role': 'SYNTHESIS', 'sentence_id': 1}
        ]
        metrics = calculator.calculate(nodes)
        
        expected = {
            ('THESIS', 'ANTITHESIS'): 1,
            ('ANTITHESIS', 'THESIS'): 1,
            ('THESIS', 'SYNTHESIS'): 1
        }
        assert metrics.transition_matrix == expected
    
    def test_calculate_density_per_sentence(self):
        """Should calculate proportion of non-OTHER roles per sentence."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 0},
            {'role': 'OTHER', 'sentence_id': 1},
            {'role': 'OTHER', 'sentence_id': 1},
            {'role': 'SYNTHESIS', 'sentence_id': 2},
            {'role': 'OTHER', 'sentence_id': 2}
        ]
        metrics = calculator.calculate(nodes)
        assert metrics.density_per_sentence == [1.0, 0.0, 0.5]
    
    def test_calculate_full_example(self):
        """Should calculate all metrics correctly for realistic example."""
        calculator = MetricsCalculator()
        nodes = [
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'THESIS', 'sentence_id': 0},
            {'role': 'ANTITHESIS', 'sentence_id': 1},
            {'role': 'OTHER', 'sentence_id': 1},
            {'role': 'SYNTHESIS', 'sentence_id': 2}
        ]
        metrics = calculator.calculate(nodes)
        
        assert metrics.total_nodes == 5
        assert metrics.role_counts == {
            'THESIS': 2, 'ANTITHESIS': 1, 'OTHER': 1, 'SYNTHESIS': 1
        }
        assert metrics.transition_matrix == {
            ('THESIS', 'THESIS'): 1, ('THESIS', 'ANTITHESIS'): 1,
            ('ANTITHESIS', 'OTHER'): 1, ('OTHER', 'SYNTHESIS'): 1
        }
        assert metrics.density_per_sentence == [1.0, 0.5, 1.0]
