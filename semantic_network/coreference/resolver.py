"""Coreference resolution with neural and heuristic methods."""

from typing import List, Set, Tuple
from ..relations.edge_factory import Edge, create_coref_edge


class CoreferenceResolver:
    """Resolves coreferences using neural and heuristic methods."""
    
    def __init__(self):
        self.neural_chains = []
        self.heuristic_pairs = []
        self.merged_edges = set()
    
    def add_neural_chain(self, chain: List[str]):
        """
        Add a neural coreference chain.
        
        Args:
            chain: List of coreferent mentions in order
        """
        self.neural_chains.append(chain)
    
    def add_heuristic_pair(self, antecedent: str, anaphor: str):
        """
        Add a heuristic coreference pair.
        
        Args:
            antecedent: The antecedent mention
            anaphor: The anaphor mention
        """
        self.heuristic_pairs.append((antecedent, anaphor))
    
    def _chain_to_edges(self, chain: List[str], source: str = "neural") -> Set[Edge]:
        """
        Convert a coreference chain to edges.
        
        Edge direction: antecedent -> anaphor
        Each mention points to the next in the chain.
        
        Args:
            chain: Ordered list of mentions
            source: Source of resolution ("neural" or "heuristic")
            
        Returns:
            Set of coreference edges
        """
        edges = set()
        for i in range(len(chain) - 1):
            edge = create_coref_edge(chain[i], chain[i + 1], source)
            edges.add(edge)
        return edges
    
    def _is_duplicate(self, edge: Edge, existing_edges: Set[Edge]) -> bool:
        """
        Check if an edge is a duplicate.
        
        Args:
            edge: Edge to check
            existing_edges: Set of existing edges
            
        Returns:
            True if duplicate exists
        """
        for existing in existing_edges:
            if (existing.source == edge.source and 
                existing.target == edge.target and 
                existing.edge_type == edge.edge_type):
                return True
        return False
    
    def merge_and_resolve(self) -> List[Edge]:
        """
        Merge neural chains and heuristic pairs without duplication.
        
        Process:
        1. Convert neural chains to edges
        2. Add heuristic pairs as edges
        3. Skip duplicates when merging
        
        Returns:
            List of unique coreference edges
        """
        # First, add all neural chain edges
        for chain in self.neural_chains:
            neural_edges = self._chain_to_edges(chain, "neural")
            self.merged_edges.update(neural_edges)
        
        # Then merge heuristic pairs, avoiding duplicates
        for antecedent, anaphor in self.heuristic_pairs:
            heuristic_edge = create_coref_edge(antecedent, anaphor, "heuristic")
            
            # Only add if not a duplicate
            if not self._is_duplicate(heuristic_edge, self.merged_edges):
                self.merged_edges.add(heuristic_edge)
        
        return list(self.merged_edges)
    
    def get_chains(self) -> List[List[str]]:
        """Get neural coreference chains."""
        return self.neural_chains
    
    def get_heuristic_pairs(self) -> List[Tuple[str, str]]:
        """Get heuristic coreference pairs."""
        return self.heuristic_pairs
