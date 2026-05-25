"""
Tests for the Huffman implementation.

These tests verify:
    1. Each phase is correct in isolation.
    2. Encode/decode round-trips perfectly.
    3. The Huffman average code length is within < 1 bit of Shannon entropy.
       (This is THE THEOREM we discussed — proving it empirically here.)
"""
from __future__ import annotations
import math
import random
import string
import pytest

from src.frequency import (
    count_frequencies,
    empirical_probabilities,
    shannon_entropy,
)
from src.tree import build_tree, tree_depths
from src.codes import (
    build_code_map,
    verify_prefix_property,
    average_code_length,
)
from src.encode import encode, serialize_tree, bits_to_bytes
from src.decode import decode, deserialize_tree, bytes_to_bits


# ---------------------------------------------------------------------------
# Phase 1: Frequencies and entropy
# ---------------------------------------------------------------------------

class TestFrequency:
    def test_empty(self):
        assert count_frequencies(b"") == {}

    def test_single_byte(self):
        assert count_frequencies(b"a") == {97: 1}

    def test_repeated(self):
        assert count_frequencies(b"aaaa") == {97: 4}

    def test_mixed(self):
        assert count_frequencies(b"abca") == {97: 2, 98: 1, 99: 1}

    def test_all_256_byte_values(self):
        data = bytes(range(256))
        freqs = count_frequencies(data)
        assert len(freqs) == 256
        assert all(c == 1 for c in freqs.values())


class TestProbabilities:
    def test_empty(self):
        assert empirical_probabilities({}) == {}

    def test_sums_to_one(self):
        probs = empirical_probabilities({1: 2, 2: 3, 3: 5})
        assert abs(sum(probs.values()) - 1.0) < 1e-9

    def test_proportional(self):
        probs = empirical_probabilities({1: 1, 2: 3})
        assert abs(probs[1] - 0.25) < 1e-9
        assert abs(probs[2] - 0.75) < 1e-9


class TestEntropy:
    def test_empty_is_zero(self):
        assert shannon_entropy({}) == 0.0

    def test_single_symbol_is_zero(self):
        # If we KNOW which symbol comes next, no information is conveyed.
        assert shannon_entropy({97: 100}) == 0.0

    def test_uniform_two_symbols_is_one_bit(self):
        # Fair coin flip = exactly 1 bit of entropy.
        assert abs(shannon_entropy({0: 50, 1: 50}) - 1.0) < 1e-9

    def test_uniform_n_symbols_is_log2_n(self):
        # 8 equiprobable symbols = log_2(8) = 3 bits.
        freqs = {i: 1 for i in range(8)}
        assert abs(shannon_entropy(freqs) - 3.0) < 1e-9

    def test_biased_coin_is_low(self):
        # 99/1 split is very predictable; entropy << 1 bit.
        H = shannon_entropy({0: 99, 1: 1})
        assert H < 0.1


# ---------------------------------------------------------------------------
# Phase 2: Tree
# ---------------------------------------------------------------------------

class TestTree:
    def test_empty(self):
        assert build_tree({}) is None

    def test_single_symbol_is_a_leaf(self):
        root = build_tree({97: 5})
        assert root is not None
        assert root.is_leaf
        assert root.symbol == 97

    def test_total_frequency_is_preserved(self):
        freqs = {ord('a'): 5, ord('b'): 9, ord('c'): 12, ord('d'): 13}
        root = build_tree(freqs)
        assert root.freq == sum(freqs.values())

    def test_more_frequent_symbol_has_smaller_depth(self):
        # Classic Huffman example with skewed frequencies.
        freqs = {ord('a'): 50, ord('b'): 5, ord('c'): 1}
        root = build_tree(freqs)
        depths = tree_depths(root)
        assert depths[ord('a')] < depths[ord('b')]
        assert depths[ord('b')] <= depths[ord('c')]


# ---------------------------------------------------------------------------
# Phase 3: Codes
# ---------------------------------------------------------------------------

class TestCodes:
    def test_empty(self):
        assert build_code_map(None) == {}

    def test_single_symbol_gets_one_bit(self):
        root = build_tree({97: 10})
        codes = build_code_map(root)
        assert codes == {97: "0"}

    def test_prefix_property_holds(self):
        # Random distribution; prefix property MUST hold.
        random.seed(42)
        freqs = {b: random.randint(1, 100) for b in range(20)}
        root = build_tree(freqs)
        codes = build_code_map(root)
        assert verify_prefix_property(codes)

    def test_codes_only_zeros_and_ones(self):
        freqs = {ord('a'): 5, ord('b'): 9, ord('c'): 12}
        codes = build_code_map(build_tree(freqs))
        for code in codes.values():
            assert all(c in "01" for c in code)


# ---------------------------------------------------------------------------
# Phase 4 + 5: Encode / decode round trips
# ---------------------------------------------------------------------------

class TestRoundTrip:
    """Every input should decode back to itself."""

    @pytest.mark.parametrize("data", [
        b"",
        b"a",
        b"aaaa",
        b"abcdefg",
        b"the quick brown fox jumps over the lazy dog",
        b"\x00\x01\x02\x03\x04\xff\xfe\xfd",
        bytes(range(256)),                  # all byte values
        b"a" * 1000 + b"b" * 100 + b"c",    # skewed
    ])
    def test_round_trip(self, data: bytes):
        assert decode(encode(data)) == data

    def test_random_bytes(self):
        random.seed(123)
        for _ in range(20):
            n = random.randint(0, 5000)
            data = bytes(random.randint(0, 255) for _ in range(n))
            assert decode(encode(data)) == data

    def test_english_text(self):
        data = (
            b"It was the best of times, it was the worst of times, "
            b"it was the age of wisdom, it was the age of foolishness, "
            b"it was the epoch of belief, it was the epoch of incredulity, "
        ) * 50
        assert decode(encode(data)) == data


# ---------------------------------------------------------------------------
# The big one: Shannon's theorem in action
# ---------------------------------------------------------------------------

class TestShannonBound:
    """
    These tests verify the central theorem:
        Huffman's average code length L satisfies  H <= L < H + 1.

    The lower bound H is Shannon's source coding theorem (you CANNOT do
    better lossless). The upper bound H+1 is Huffman's specific guarantee.
    """

    def test_huffman_meets_shannon_lower_bound(self):
        # On any distribution, Huffman L >= H.
        random.seed(7)
        for _ in range(10):
            freqs = {b: random.randint(1, 1000) for b in range(random.randint(2, 50))}
            root = build_tree(freqs)
            codes = build_code_map(root)
            L = average_code_length(codes, freqs)
            H = shannon_entropy(freqs)
            assert L >= H - 1e-9, f"L={L} < H={H} — violates Shannon!"

    def test_huffman_within_one_bit_of_entropy(self):
        # Huffman's guarantee: L < H + 1.
        random.seed(11)
        for _ in range(10):
            freqs = {b: random.randint(1, 1000) for b in range(random.randint(2, 50))}
            root = build_tree(freqs)
            codes = build_code_map(root)
            L = average_code_length(codes, freqs)
            H = shannon_entropy(freqs)
            assert L < H + 1, f"L={L} exceeds H+1={H+1} — Huffman is broken!"

    def test_dyadic_distribution_achieves_entropy_exactly(self):
        # When p_i = 1/2^k for all i, Huffman matches H EXACTLY.
        # Example: {a: 1/2, b: 1/4, c: 1/8, d: 1/8} -> H = 1.75 bits.
        freqs = {ord('a'): 4, ord('b'): 2, ord('c'): 1, ord('d'): 1}
        L = average_code_length(build_code_map(build_tree(freqs)), freqs)
        H = shannon_entropy(freqs)
        assert abs(L - H) < 1e-9
        assert abs(H - 1.75) < 1e-9

    def test_uniform_random_bytes_cannot_be_compressed(self):
        # Maximum-entropy input (uniform over 256 byte values).
        # H = 8 bits/byte exactly. Huffman uses 8 bits/byte. No compression.
        # This is why encrypted data is incompressible.
        random.seed(99)
        data = bytes(random.randint(0, 255) for _ in range(10000))
        freqs = count_frequencies(data)
        H = shannon_entropy(freqs)
        L = average_code_length(build_code_map(build_tree(freqs)), freqs)
        assert H > 7.9   # essentially 8
        assert L > 7.9
        assert L < 8.05  # might be exactly 8

    def test_english_text_compresses_well(self):
        # English has H ≈ 4-5 bits/char (vs 8 raw).
        # Huffman should land in roughly the same neighborhood.
        text = (
            "the quick brown fox jumps over the lazy dog. "
            "pack my box with five dozen liquor jugs. "
            "how vexingly quick daft zebras jump! "
        ) * 200
        data = text.encode("utf-8")
        freqs = count_frequencies(data)
        H = shannon_entropy(freqs)
        L = average_code_length(build_code_map(build_tree(freqs)), freqs)
        assert 3.5 < H < 5.0     # English entropy range
        assert L < 5.0           # Huffman gets close


# ---------------------------------------------------------------------------
# Bit / tree serialization plumbing
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_bits_bytes_roundtrip(self):
        bits = "1010110011110000"
        assert bytes_to_bits(bits_to_bytes(bits), len(bits)) == bits

    def test_bits_bytes_with_padding(self):
        bits = "10101"  # not byte-aligned
        recovered = bytes_to_bits(bits_to_bytes(bits), len(bits))
        assert recovered == bits

    def test_tree_serialization_roundtrip(self):
        freqs = {ord('a'): 5, ord('b'): 9, ord('c'): 12, ord('d'): 13, ord('e'): 16}
        root = build_tree(freqs)
        serialized = serialize_tree(root)
        rebuilt, _ = deserialize_tree(serialized, 0)
        assert tree_depths(root) == tree_depths(rebuilt)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
