"""Tests for relation builder with temporal and discourse markers."""

import pytest
from semantic_network.relations.relation_builder import RelationBuilder, DISCOURSE_MARKERS
from semantic_network.relations.edge_factory import EdgeType


class TestTemporalEdges:
    """Test temporal edge direction correctness."""
    
    def test_before_edge_direction(self):
        """Test 'X before Y' creates edge X -> Y."""
        builder = RelationBuilder()
        edge = builder.add_temporal_relation("event1 before event2", "event1", "event2")
        
        assert edge.source == "event1"
        assert edge.target == "event2"
        assert edge.edge_type == EdgeType.TEMPORAL
    
    def test_after_edge_direction(self):
        """Test 'X after Y' creates edge Y -> X."""
        builder = RelationBuilder()
        edge = builder.add_temporal_relation("event1 after event2", "event1", "event2")
        
        # After reverses: event1 after event2 means event2 -> event1
        assert edge.source == "event2"
        assert edge.target == "event1"
        assert edge.edge_type == EdgeType.TEMPORAL
    
    def test_before_in_sentence(self):
        """Test before detection in full sentence."""
        builder = RelationBuilder()
        edge = builder.add_temporal_relation(
            "The meeting happened before the deadline",
            "meeting", "deadline"
        )
        assert edge.source == "meeting"
        assert edge.target == "deadline"
    
    def test_after_in_sentence(self):
        """Test after detection in full sentence."""
        builder = RelationBuilder()
        edge = builder.add_temporal_relation(
            "The celebration came after the victory",
            "celebration", "victory"
        )
        assert edge.source == "victory"
        assert edge.target == "celebration"


class TestMultiWordDiscourseMarkers:
    """Test multi-word discourse marker detection."""
    
    def test_even_though_concession(self):
        """Test 'even though' detected as CONCESSION."""
        builder = RelationBuilder()
        marker, edge_type = builder.detect_discourse_marker("even though it rained")
        
        assert marker == "even though"
        assert edge_type == EdgeType.CONCESSION
    
    def test_in_spite_of_concession(self):
        """Test 'in spite of' detected as CONCESSION."""
        builder = RelationBuilder()
        marker, edge_type = builder.detect_discourse_marker("in spite of the weather")
        
        assert marker == "in spite of"
        assert edge_type == EdgeType.CONCESSION
    
    def test_as_well_as_elaboration(self):
        """Test 'as well as' detected as ELABORATION."""
        builder = RelationBuilder()
        marker, edge_type = builder.detect_discourse_marker("coffee as well as tea")
        
        assert marker == "as well as"
        assert edge_type == EdgeType.ELABORATION
    
    def test_in_order_to_purpose(self):
        """Test 'in order to' detected as PURPOSE."""
        builder = RelationBuilder()
        marker, edge_type = builder.detect_discourse_marker("in order to succeed")
        
        assert marker == "in order to"
        assert edge_type == EdgeType.PURPOSE
    
    def test_multi_word_priority(self):
        """Test multi-word markers checked before single words."""
        builder = RelationBuilder()
        # Should match "in order to" not just "to"
        marker, edge_type = builder.detect_discourse_marker("in order to win")
        
        assert marker == "in order to"
        assert edge_type == EdgeType.PURPOSE


class TestRelationBuilding:
    """Test complete relation building."""
    
    def test_build_with_concession(self):
        """Test building relation with concession marker."""
        builder = RelationBuilder()
        edge = builder.build_relation("even though X, Y", "X", "Y")
        
        assert edge.edge_type == EdgeType.CONCESSION
        assert edge.source == "X"
        assert edge.target == "Y"
    
    def test_build_with_temporal(self):
        """Test building temporal relation."""
        builder = RelationBuilder()
        edge = builder.build_relation("X before Y", "X", "Y")
        
        assert edge.edge_type == EdgeType.TEMPORAL
        assert edge.source == "X"
        assert edge.target == "Y"
    
    def test_edges_accumulate(self):
        """Test that edges accumulate in builder."""
        builder = RelationBuilder()
        builder.build_relation("X before Y", "X", "Y")
        builder.build_relation("A after B", "A", "B")
        
        edges = builder.get_edges()
        assert len(edges) == 2
