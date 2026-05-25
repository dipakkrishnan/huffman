"""
The payoff. Run this on any file to see Huffman approach Shannon's bound.

This is where the entire log intuition becomes a number you can stare at.
"""
from __future__ import annotations
import sys
from .frequency import count_frequencies, shannon_entropy
from .tree import build_tree
from .codes import build_code_map, average_code_length
from .encode import encode


def report(filepath: str) -> None:
    with open(filepath, "rb") as f:
        data = f.read()

    n = len(data)
    if n == 0:
        print(f"{filepath} is empty.")
        return

    freqs = count_frequencies(data)
    H = shannon_entropy(freqs)

    root = build_tree(freqs)
    codes = build_code_map(root)
    L = average_code_length(codes, freqs)

    compressed = encode(data)
    overhead_bits = (len(compressed) * 8) - (L * n)

    print(f"File:                  {filepath}")
    print(f"Size:                  {n:,} bytes ({n*8:,} bits)")
    print(f"Unique symbols:        {len(freqs)}")
    print(f"Shannon entropy H:     {H:.4f} bits/symbol  (the floor)")
    print(f"Huffman avg code len:  {L:.4f} bits/symbol  (your result)")
    print(f"Gap from optimal:      {L - H:.4f} bits/symbol")
    print(f"                       (theory guarantees < 1 bit)")
    print(f"Compressed size:       {len(compressed):,} bytes "
          f"({100*len(compressed)/n:.1f}% of original)")
    print(f"Header overhead:       {int(overhead_bits):,} bits")
    print()
    print("Top 10 most frequent symbols (code length should track -log_2(p)):")
    print(f"{'symbol':>10} {'freq':>8} {'p':>10} {'-log2(p)':>10} {'code len':>10}")
    import math
    top = sorted(freqs.items(), key=lambda x: -x[1])[:10]
    for sym, freq in top:
        p = freq / n
        info = -math.log2(p) if p > 0 else 0
        code_len = len(codes[sym])
        # Render printable chars nicely; show byte value for non-printable
        if 32 <= sym < 127:
            label = repr(chr(sym))
        else:
            label = f"\\x{sym:02x}"
        print(f"{label:>10} {freq:>8} {p:>10.4f} {info:>10.3f} {code_len:>10}")


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python -m src.verify <file>", file=sys.stderr)
        sys.exit(1)
    report(sys.argv[1])


if __name__ == "__main__":
    main()
