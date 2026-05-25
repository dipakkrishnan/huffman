"""
Phase 4: Encode bytes -> compressed bytes.

Output format:
    [4 bytes: bit-length of serialized tree (big-endian uint32)]
    [serialized tree, bit-packed and padded to byte boundary]
    [4 bytes: bit-length of payload (big-endian uint32)]
    [encoded payload, bit-packed and padded to byte boundary]

Tree serialization (recursive):
    Leaf:    '1' + 8 bits of the symbol's byte value
    Internal: '0' + serialize(left) + serialize(right)

This is a pre-order traversal. The decoder reconstructs the tree by
reading the same sequence and recursing.

Bit-packing:
    Build a string of '0's and '1's, then pack 8 at a time.
    The final byte may be padded with zeros — that's why we store the
    EXACT bit length up front.
"""
from __future__ import annotations
from typing import Dict, Optional
from .frequency import count_frequencies
from .tree import Node, build_tree
from .codes import build_code_map


def serialize_tree(root: Optional[Node]) -> str:
    """Convert a tree into a string of '0' and '1' characters."""
    if root is None:
        return ""
    if root.is_leaf:
        # 8 bits = 1 byte; format the symbol as exactly 8 bits.
        # TODO: return '1' + 8-bit binary representation of root.symbol
        raise NotImplementedError
    # TODO: '0' + serialize_tree(left) + serialize_tree(right)
    raise NotImplementedError


def bits_to_bytes(bits: str) -> bytes:
    """Pack a string of '0'/'1' into bytes, padding the last byte with zeros.

    The caller is responsible for storing the original bit length so the
    decoder knows where the real data ends.
    """
    # Pad to a multiple of 8.
    pad_len = (8 - len(bits) % 8) % 8
    bits_padded = bits + "0" * pad_len

    out = bytearray()
    # TODO: walk 8 chars at a time, convert each to a byte with int(chunk, 2).
    raise NotImplementedError
    return bytes(out)


def encode(data: bytes) -> bytes:
    """Compress data using Huffman coding.

    Layout:
        [4 bytes tree_bit_len][tree_bytes][4 bytes data_bit_len][data_bytes]

    Edge cases:
        - Empty data: return an 8-byte header with all zeros.
    """
    if not data:
        return (0).to_bytes(4, "big") + (0).to_bytes(4, "big")

    freqs = count_frequencies(data)
    root = build_tree(freqs)
    codes = build_code_map(root)

    tree_bits = serialize_tree(root)
    payload_bits = "".join(codes[b] for b in data)

    tree_bytes = bits_to_bytes(tree_bits)
    payload_bytes = bits_to_bytes(payload_bits)

    # TODO: concatenate the 4-byte length headers + bodies.
    raise NotImplementedError


def main() -> None:
    """CLI: python -m src.encode <file> > <out>"""
    import sys
    if len(sys.argv) != 2:
        print("usage: python -m src.encode <input_file> > <output_file>",
              file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    compressed = encode(data)
    sys.stdout.buffer.write(compressed)


if __name__ == "__main__":
    main()
