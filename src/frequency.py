"""
Phase 1: Frequency counting.

The first step in Huffman is to measure the empirical probability
distribution of symbols. Frequencies → probabilities → information content.

For a symbol with probability p, its Shannon information content is
    I(symbol) = -log_2(p)  bits

Frequent symbols carry little information; rare symbols carry a lot.
Huffman assigns code lengths that approximate I(symbol).
"""
from __future__ import annotations
from collections import Counter
from typing import Dict
import math


def count_frequencies(data: bytes) -> Dict[int, int]:
    """Return a dict mapping each byte value (0-255) to its count in data.

    Args:
        data: input bytes

    Returns:
        dict: byte value -> count. Bytes not in the input are NOT in the dict.

    Examples:
        >>> count_frequencies(b"abca")
        {97: 2, 98: 1, 99: 1}
        >>> count_frequencies(b"")
        {}
    """
    # TODO: implement. One line with collections.Counter.
    return dict(Counter(data))


def empirical_probabilities(freqs: Dict[int, int]) -> Dict[int, float]:
    """Convert frequencies to probabilities (each p_i in [0, 1], sum = 1)."""
    total = sum(freqs.values())
    if total == 0:
        return {}
    probs = {}
    for key in freqs:
        probs[key] = freqs[key] / total
    return probs


def shannon_entropy(freqs: Dict[int, int]) -> float:
    """Compute Shannon entropy H = -sum(p_i * log_2(p_i)) in bits per symbol.

    This is the THEORETICAL LOWER BOUND on average bits/symbol for any
    lossless code. Huffman gets within < 1 bit of this.

    Edge cases:
        - Empty input: return 0.0
        - Single symbol (p=1): return 0.0 (no uncertainty -> no information)
    """
    probs = empirical_probabilities(freqs)
    entropy = 0
    for key in probs:
        v = probs[key]
        entropy += v * math.log2(v)
    return -1*entropy
