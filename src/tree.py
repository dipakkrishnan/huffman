"""
Phase 2: Build the Huffman tree.

Algorithm (Huffman 1952):
    1. Each symbol starts as a leaf node, weighted by its frequency.
    2. Insert all leaves into a min-priority-queue (heap).
    3. While >1 node remains:
         pop the two smallest (a, b)
         create a new internal node with frequency a.freq + b.freq
         left = a, right = b
         push it back
    4. The last remaining node is the root.

Why this works (intuition):
    The two LEAST frequent symbols MUST be at the deepest level of any
    optimal prefix tree. (If not, we could swap them with deeper siblings
    and reduce total cost.) Huffman exploits this by always merging the
    two smallest weights — they become siblings at max depth.

The tree's depth at each leaf is the code length for that symbol.
Code length should approximate -log_2(p_i). For dyadic distributions
(p_i = 1/2^k for all i), Huffman matches Shannon EXACTLY.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict
import heapq
import itertools


@dataclass
class Node:
    """A node in the Huffman tree.

    Leaves have a symbol (a byte value 0-255). Internals do not.
    """
    freq: int
    symbol: Optional[int] = None        # None for internal nodes
    left: Optional["Node"] = None
    right: Optional["Node"] = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


def build_tree(freqs: Dict[int, int]) -> Optional[Node]:
    """Build a Huffman tree from byte frequencies. Return the root.

    Edge cases:
        - Empty freqs: return None.
        - Single symbol: return a single leaf node. (Special-cased downstream
          so the code map can still assign it a 1-bit code.)

    Examples:
        >>> root = build_tree({ord('a'): 5, ord('b'): 1, ord('c'): 1})
        >>> root.freq  # total
        7
        >>> root.is_leaf
        False
    """
    if not freqs:
        return None

    # The tiebreaker counter is crucial. Python's heapq compares tuples
    # element-by-element. If two have equal freq, it'd try to compare
    # Node objects (which aren't orderable), raising TypeError.
    # The counter guarantees we never compare Nodes.
    counter = itertools.count()
    heap: list = []

    # TODO: push one (freq, tiebreaker_id, leaf_node) tuple per symbol
    raise NotImplementedError

    # TODO: while len(heap) > 1, pop two smallest, merge into a parent,
    # push the parent back. Return the last node's Node when done.


def tree_depths(root: Optional[Node]) -> Dict[int, int]:
    """Return a dict mapping each leaf's symbol to its depth in the tree.

    Depth == code length for that symbol.

    Useful for verifying that frequent symbols got shorter codes than rare ones.
    """
    if root is None:
        return {}
    result: Dict[int, int] = {}
    # TODO: recursive walk. Special-case a single-leaf tree
    # (give it depth 1, since we still need at least 1 bit to encode it).
    raise NotImplementedError
