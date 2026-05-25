"""
Phase 3: Tree -> code map.

Walk the tree from root to each leaf. At each step, append:
    '0' if you took the left branch
    '1' if you took the right branch

The accumulated string at a leaf IS that symbol's code.

The PREFIX PROPERTY: no code is a prefix of another. This holds for
Huffman codes because all symbols are at LEAVES — paths from root to
distinct leaves diverge at some internal node, so neither path can be
a prefix of the other.

This is what makes the encoding self-delimiting: a decoder walking
bit-by-bit ALWAYS knows exactly when it has read a complete symbol.

Connection to the log intuition:
    A code of length L can distinguish 2^L outcomes.
    Symbols with probability p need codes of length ~ -log_2(p) bits
    to be optimal. Frequent symbols get short codes; rare get long.
"""
from __future__ import annotations
from typing import Dict, Optional
from .tree import Node


def build_code_map(root: Optional[Node]) -> Dict[int, str]:
    """Walk the tree and return {symbol: code_string} where code_string
    is a string of '0' and '1' characters.

    Edge cases:
        - None root: return {}.
        - Single-leaf root: return {symbol: "0"}. We need SOME code
          (1 bit) even though entropy is 0, since the file is non-empty.

    Examples:
        >>> from src.tree import build_tree
        >>> root = build_tree({ord('a'): 5, ord('b'): 1, ord('c'): 1})
        >>> codes = build_code_map(root)
        >>> sorted(codes.keys()) == [ord('a'), ord('b'), ord('c')]
        True
        >>> len(codes[ord('a')]) < len(codes[ord('b')])  # 'a' is more frequent
        True
    """
    if root is None:
        return {}

    # Special case: single-leaf tree (only one unique symbol in the input).
    if root.is_leaf:
        # TODO: return {root.symbol: "0"}
        raise NotImplementedError

    result: Dict[int, str] = {}

    def walk(node: Node, prefix: str) -> None:
        # TODO: if leaf, record prefix as the code; else recurse
        # left with prefix+"0" and right with prefix+"1".
        raise NotImplementedError

    walk(root, "")
    return result


def verify_prefix_property(codes: Dict[int, str]) -> bool:
    """Sanity check: no code in `codes` is a prefix of another.

    If Huffman is correct, this MUST be True. If it's False, decoding
    is ambiguous and the implementation has a bug.
    """
    code_list = list(codes.values())
    # TODO: O(n^2) pairwise check. For n <= 256 (bytes), this is fine.
    raise NotImplementedError


def average_code_length(codes: Dict[int, str], freqs: Dict[int, int]) -> float:
    """Compute the average code length, weighted by frequencies.

    This is what we COMPARE against Shannon entropy. It should be
    within < 1 bit of H, with equality when the distribution is dyadic
    (each p_i = 1/2^k).
    """
    total = sum(freqs.values())
    if total == 0:
        return 0.0
    # TODO: weighted average: sum(freq[s] * len(codes[s])) / total
    raise NotImplementedError
