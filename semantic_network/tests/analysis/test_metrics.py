"""Tests for dialectical metrics calculation."""

import pytest
from semantic_network.types import DialecticalRole
from semantic_network.models import SemanticNode
from semantic_network.analysis.metrics import DialecticalMetrics, MetricsCalculator


@pytest.fixture
def sample_nodes():
    """Create sample semantic nodes for testing."""
    return [
        SemanticNode(id="n1", text="thesis", sentence_index=0, position=0),
        SemanticNode(id="n2", text="statement", sentence_index=0, position=1),
        SemanticNode(id="n3", text="counter", sentence_index=1, position=0),
        SemanticNode(id="n4", text="argument", sentence_index=1, position=1),
        SemanticNode(id="n5", text="synthesis", sentence_index=2, position=0),
    ]


@pytest.fixture
def sample_assignments():
    """Create sample role assignments for testing."""
    return {
        "n1": DialecticalRole.THESIS,
        "n2": DialecticalRole.THESIS,
        "n3": DialecticalRole.ANTITHESIS,
        "n4": DialecticalRole.ANTITHESIS,
        "n5": DialecticalRole.SYNTHESIS,
    }


class TestMetricsCalculator:
    """Test suite for MetricsCalculator class."""
    
    def test_count_roles(self, sample_assignments):
        """Test role counting functionality."""
        calculator = MetricsCalculator()
        counts = calculator._count_roles(sample_assignments)
        
        assert counts[DialecticalRole.THESIS] == 2
        assert counts[DialecticalRole.ANTITHESIS] == 2
        assert counts[DialecticalRole.SYNTHESIS] == 1
        assert counts[DialecticalRole.UNASSIGNED] == 0
    
    def test_compute_proportions(self):
        """Test proportion calculation."""
        calculator = MetricsCalculator()
        counts = {
            DialecticalRole.THESIS: 2,
            DialecticalRole.ANTITHESIS: 2,
            DialecticalRole.SYNTHESIS: 1,
            DialecticalRole.UNASSIGNED: 0,
        }
        
        proportions = calculator._compute_proportions(counts)
        
        assert proportions[DialecticalRole.THESIS] == 0.4
        assert proportions[DialecticalRole.ANTITHESIS] == 0.4
        assert proportions[DialecticalRole.SYNTHESIS] == 0.2
        assert proportions[DialecticalRole.UNASSIGNED] == 0.0
    
    def test_compute_proportions_empty(self):
        """Test proportion calculation with empty input."""
        calculator = MetricsCalculator()
        counts = {role: 0 for role in DialecticalRole}
        
        proportions = calculator._compute_proportions(counts)
        
        assert all(prop == 0.0 for prop in proportions.values())
    
    def test_build_transition_matrix(self, sample_nodes, sample_assignments):
        """Test transition matrix construction."""
        calculator = MetricsCalculator()
        matrix = calculator._build_transition_matrix(sample_assignments, sample_nodes)
        
        # Verify matrix structure
        assert len(matrix) == len(DialecticalRole)
        for role in DialecticalRole:
            assert len(matrix[role]) == len(DialecticalRole)
        
        # Verify specific transitions based on node order
        # n1 (THESIS) -> n2 (THESIS)
        assert matrix[DialecticalRole.THESIS][DialecticalRole.THESIS] == 1
        # n2 (THESIS) -> n3 (ANTITHESIS)
        assert matrix[DialecticalRole.THESIS][DialecticalRole.ANTITHESIS] == 1
        # n3 (ANTITHESIS) -> n4 (ANTITHESIS)
        assert matrix[DialecticalRole.ANTITHESIS][DialecticalRole.ANTITHESIS] == 1
        # n4 (ANTITHESIS) -> n5 (SYNTHESIS)
        assert matrix[DialecticalRole.ANTITHESIS][DialecticalRole.SYNTHESIS] == 1
    
    def test_compute_density(self, sample_nodes, sample_assignments):
        """Test density calculation per sentence."""
        calculator = MetricsCalculator()
        density = calculator._compute_density(sample_assignments, sample_nodes)
        
        # All nodes in all sentences are assigned
        assert density[0] == 1.0  # 2/2 nodes assigned
        assert density[1] == 1.0  # 2/2 nodes assigned
        assert density[2] == 1.0  # 1/1 nodes assigned
    
    def test_compute_density_with_unassigned(self, sample_nodes):
        """Test density with some unassigned nodes."""
        calculator = MetricsCalculator()
        assignments = {
            "n1": DialecticalRole.THESIS,
            # n2 is unassigned
            "n3": DialecticalRole.ANTITHESIS,
            # n4 is unassigned
            "n5": DialecticalRole.SYNTHESIS,
        }
        
        density = calculator._compute_density(assignments, sample_nodes)
        
        assert density[0] == 0.5  # 1/2 nodes assigned
        assert density[1] == 0.5  # 1/2 nodes assigned
        assert density[2] == 1.0  # 1/1 nodes assigned
    
    def test_calculate_full_metrics(self, sample_nodes, sample_assignments):
        """Test complete metrics calculation."""
        calculator = MetricsCalculator()
        metrics = calculator.calculate(sample_assignments, sample_nodes)
        
        # Verify metrics object structure
        assert isinstance(metrics, DialecticalMetrics)
        assert isinstance(metrics.role_counts, dict)
        assert isinstance(metrics.role_proportions, dict)
        assert isinstance(metrics.transition_matrix, dict)
        assert isinstance(metrics.density_by_sentence, dict)
        
        # Verify counts
        assert metrics.role_counts[DialecticalRole.THESIS] == 2
        assert metrics.role_counts[DialecticalRole.ANTITHESIS] == 2
        assert metrics.role_counts[DialecticalRole.SYNTHESIS] == 1
        
        # Verify proportions sum to 1.0
        assert abs(sum(metrics.role_proportions.values()) - 1.0) < 0.0001
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        calculator = MetricsCalculator()
        metrics = calculator.calculate({}, [])
        
        assert all(count == 0 for count in metrics.role_counts.values())
        assert all(prop == 0.0 for prop in metrics.role_proportions.values())
        assert len(metrics.density_by_sentence) == 0
