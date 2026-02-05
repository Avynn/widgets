"""Tests for coreference resolver with merging and alignment."""

import pytest
from semantic_network.coreference.resolver import CoreferenceResolver
from semantic_network.relations.edge_factory import EdgeType


class TestCorefEdgeDirection:
    """Test coreference edge direction alignment."""
    
    def test_antecedent_to_anaphor(self):
        """Test edges point from antecedent to anaphor."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["John", "he", "him"])
        
        edges = resolver.merge_and_resolve()
        
        # Check edge pairs (order may vary due to set)
        edge_pairs = {(e.source, e.target) for e in edges}
        assert ("John", "he") in edge_pairs
        assert ("he", "him") in edge_pairs
    
    def test_chain_order_preserved(self):
        """Test chain order determines edge direction."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["Mary", "she", "her"])
        
        edges = resolver.merge_and_resolve()
        
        assert len(edges) == 2
        # Find the edges (order may vary due to set)
        edge_pairs = {(e.source, e.target) for e in edges}
        assert ("Mary", "she") in edge_pairs
        assert ("she", "her") in edge_pairs


class TestResolutionSourceMetadata:
    """Test metadata field for resolution source."""
    
    def test_neural_source_metadata(self):
        """Test neural edges have 'neural' source metadata."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["Alice", "she"])
        
        edges = resolver.merge_and_resolve()
        
        assert edges[0].metadata["source"] == "neural"
    
    def test_heuristic_source_metadata(self):
        """Test heuristic edges have 'heuristic' source metadata."""
        resolver = CoreferenceResolver()
        resolver.add_heuristic_pair("Bob", "he")
        
        edges = resolver.merge_and_resolve()
        
        assert edges[0].metadata["source"] == "heuristic"


class TestMergingWithoutDuplication:
    """Test merging heuristic pairs with neural chains."""
    
    def test_merge_non_overlapping(self):
        """Test merging when no overlap exists."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["John", "he"])
        resolver.add_heuristic_pair("Mary", "she")
        
        edges = resolver.merge_and_resolve()
        
        assert len(edges) == 2
        # Should have both pairs
        sources = {e.source for e in edges}
        assert "John" in sources
        assert "Mary" in sources
    
    def test_merge_with_duplication(self):
        """Test that duplicate pairs are not added."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["John", "he"])
        # Try to add same pair heuristically
        resolver.add_heuristic_pair("John", "he")
        
        edges = resolver.merge_and_resolve()
        
        # Should only have 1 edge, not 2
        assert len(edges) == 1
        assert edges[0].metadata["source"] == "neural"
    
    def test_merge_partial_overlap(self):
        """Test merging with partial overlap in chains."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["Alice", "she", "her"])
        # Add a heuristic pair that matches part of the chain
        resolver.add_heuristic_pair("Alice", "she")
        # Add a new heuristic pair not in chain
        resolver.add_heuristic_pair("Bob", "him")
        
        edges = resolver.merge_and_resolve()
        
        # Should have 2 from neural + 1 new from heuristic = 3 total
        assert len(edges) == 3
    
    def test_neural_chains_processed_first(self):
        """Test neural chains are added before heuristic pairs."""
        resolver = CoreferenceResolver()
        # Add heuristic first
        resolver.add_heuristic_pair("X", "Y")
        # Add neural with same pair
        resolver.add_neural_chain(["X", "Y"])
        
        edges = resolver.merge_and_resolve()
        
        # Should only have 1 edge, from neural (processed first)
        assert len(edges) == 1
        assert edges[0].metadata["source"] == "neural"


class TestMultipleChains:
    """Test handling multiple neural chains."""
    
    def test_multiple_neural_chains(self):
        """Test multiple neural chains are all processed."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["John", "he"])
        resolver.add_neural_chain(["Mary", "she"])
        
        edges = resolver.merge_and_resolve()
        
        assert len(edges) == 2
        sources = {e.source for e in edges}
        assert "John" in sources
        assert "Mary" in sources
    
    def test_long_chain(self):
        """Test longer coreference chains."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["Dr. Smith", "the doctor", "she", "her"])
        
        edges = resolver.merge_and_resolve()
        
        # 4 mentions = 3 edges
        assert len(edges) == 3
        edge_pairs = {(e.source, e.target) for e in edges}
        assert ("Dr. Smith", "the doctor") in edge_pairs
        assert ("the doctor", "she") in edge_pairs
        assert ("she", "her") in edge_pairs


class TestEdgeType:
    """Test all coref edges have correct type."""
    
    def test_all_edges_are_coref_type(self):
        """Test all edges have COREFERENCE type."""
        resolver = CoreferenceResolver()
        resolver.add_neural_chain(["X", "Y", "Z"])
        resolver.add_heuristic_pair("A", "B")
        
        edges = resolver.merge_and_resolve()
        
        for edge in edges:
            assert edge.edge_type == EdgeType.COREFERENCE
