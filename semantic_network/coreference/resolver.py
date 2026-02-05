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
        """Add a neural coreference chain."""
        self.neural_chains.append(chain)
    
    def add_heuristic_pair(self, antecedent: str, anaphor: str):
        """Add a heuristic coreference pair."""
        self.heuristic_pairs.append((antecedent, anaphor))
    
    def _chain_to_edges(self, chain: List[str], source: str = "neural") -> Set[Edge]:
        """Convert coreference chain to edges (antecedent -> anaphor)."""
        edges = set()
        for i in range(len(chain) - 1):
            edge = create_coref_edge(chain[i], chain[i + 1], source)
            edges.add(edge)
        return edges
    
    def _is_duplicate(self, edge: Edge, existing_edges: Set[Edge]) -> bool:
        """Check if an edge is a duplicate."""
        return edge in existing_edges
    
    def merge_and_resolve(self) -> List[Edge]:
        """Merge neural chains and heuristic pairs without duplication."""
        # Add all neural chain edges first
        for chain in self.neural_chains:
            neural_edges = self._chain_to_edges(chain, "neural")
            self.merged_edges.update(neural_edges)
        
        # Merge heuristic pairs, avoiding duplicates
        for antecedent, anaphor in self.heuristic_pairs:
            heuristic_edge = create_coref_edge(antecedent, anaphor, "heuristic")
            if not self._is_duplicate(heuristic_edge, self.merged_edges):
                self.merged_edges.add(heuristic_edge)
        
        return list(self.merged_edges)
    
    def get_chains(self) -> List[List[str]]:
        """Get neural coreference chains."""
        return self.neural_chains
    
    def get_heuristic_pairs(self) -> List[Tuple[str, str]]:
        """Get heuristic coreference pairs."""
        return self.heuristic_pairs

