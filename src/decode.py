"""
Phase 5: Decode compressed bytes -> original bytes.

Process:
    1. Read tree_bit_len (4 bytes), then read that many bits and rebuild tree.
    2. Read data_bit_len (4 bytes), then walk the tree bit-by-bit.
       At each leaf, emit the symbol and reset to the root.

The prefix property guarantees this works: at each step we know exactly
where we are in the tree, and we ALWAYS reach a unique leaf for every
valid bit sequence emitted by the encoder.
"""
from __future__ import annotations
from typing import Optional, Tuple
from .tree import Node


def bytes_to_bits(data: bytes, bit_len: int) -> str:
    """Convert bytes to a string of '0'/'1', truncated to bit_len."""
    # TODO: convert each byte to 8-bit binary, concatenate, truncate.
    raise NotImplementedError


def deserialize_tree(bits: str, pos: int) -> Tuple[Optional[Node], int]:
    """Reconstruct a tree from the bit string. Returns (root, new_position).

    Mirrors `serialize_tree` exactly:
        '1' -> leaf with next 8 bits as the symbol
        '0' -> internal node, recurse left then right
    """
    if pos >= len(bits):
        return None, pos
    flag = bits[pos]
    pos += 1
    if flag == "1":
        # TODO: read 8 bits, convert to int, return Node(freq=0, symbol=val)
        # (freq doesn't matter for decoding)
        raise NotImplementedError
    else:  # '0' = internal
        # TODO: recurse left then right, build a parent, return it
        raise NotImplementedError


def decode(data: bytes) -> bytes:
    """Reverse `encode`. Return the original uncompressed bytes."""
    if len(data) < 8:
        return b""

    # Parse header.
    tree_bit_len = int.from_bytes(data[0:4], "big")
    if tree_bit_len == 0:
        return b""

    tree_byte_len = (tree_bit_len + 7) // 8
    tree_bytes = data[4 : 4 + tree_byte_len]
    tree_bits = bytes_to_bits(tree_bytes, tree_bit_len)

    root, _ = deserialize_tree(tree_bits, 0)
    if root is None:
        return b""

    # Parse the payload header.
    off = 4 + tree_byte_len
    payload_bit_len = int.from_bytes(data[off : off + 4], "big")
    payload_byte_len = (payload_bit_len + 7) // 8
    payload_bytes = data[off + 4 : off + 4 + payload_byte_len]
    payload_bits = bytes_to_bits(payload_bytes, payload_bit_len)

    out = bytearray()

    # Edge case: single-leaf tree. The payload is just "0" repeated.
    # Each "0" decodes to the single symbol.
    if root.is_leaf:
        # TODO: emit root.symbol for each bit. Use payload_bit_len, not the
        # post-padding length, so we don't emit phantom symbols from padding.
        raise NotImplementedError
        return bytes(out)

    # General case: walk the tree.
    node = root
    # TODO: for each bit in payload_bits:
    #   step left ('0') or right ('1')
    #   if at leaf: append node.symbol, reset to root
    raise NotImplementedError

    return bytes(out)


def main() -> None:
    """CLI: python -m src.decode <compressed> > <original>"""
    import sys
    if len(sys.argv) != 2:
        print("usage: python -m src.decode <input_file> > <output_file>",
              file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    sys.stdout.buffer.write(decode(data))


if __name__ == "__main__":
    main()
