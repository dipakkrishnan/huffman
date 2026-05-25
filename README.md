# Huffman coding — the log intuition, made tangible

Implement Huffman coding from scratch. Every line of this exercise pays off your information-theory intuition.

## The connection to logs

Recall: **Shannon's lower bound** says you need on average at least `H(X)` bits per symbol to encode a source with entropy `H`. For a uniform source, `H = log₂(N)`. For non-uniform, `H = -Σ pᵢ log₂(pᵢ)`.

Huffman coding **achieves this bound** (within < 1 bit per symbol) by:
1. Counting symbol frequencies → empirical probabilities `pᵢ`.
2. Assigning each symbol a code of length `≈ -log₂(pᵢ)`.
3. Frequent symbols get short codes (few bits); rare symbols get long codes.

**Why this matters**: when you finish this, run the verifier against `H` for any input file. You should see your compression ratio land within ~1% of the entropy bound — proof that you're touching the same Shannon math that justifies activation quantization on Yury's slide.

## What you'll build

```
src/
├── frequency.py     # count symbol frequencies in input
├── tree.py          # priority queue → Huffman tree
├── codes.py         # tree → {symbol: bit_string} map
├── encode.py        # bytes → compressed bytes (+ serialized tree)
├── decode.py        # compressed bytes → original bytes
└── verify.py        # compare actual bits/symbol vs Shannon entropy

tests/
└── test_huffman.py  # correctness + entropy bound tests

data/
├── tiny.txt         # for tracing by hand
├── english.txt      # English entropy ~4.1 bits/char — see Huffman approach it
└── uniform.bin      # uniform random — Huffman can't beat 8 bits/byte (proves limit!)
```

## The five phases

1. **Phase 1 — Frequencies**: `count_frequencies(data: bytes) -> dict[int, int]`. Trivial. Just `Counter`. But: this *is* your empirical probability distribution. Print it. Stare at it.

2. **Phase 2 — Tree**: build a binary tree where leaves are symbols and depth = code length. The algorithm:
   ```
   Put each (frequency, symbol) into a min-heap.
   Repeat until 1 node left:
       Pop the two smallest.
       Combine into a new node with summed frequency.
       Push back into heap.
   ```
   **The magic**: this *greedy* algorithm provably produces the optimal prefix code. The proof is gorgeous — see Cormen et al. The two least-frequent symbols *must* be siblings at max depth in any optimal tree.

3. **Phase 3 — Code map**: walk the tree, accumulating a bit string. Left = '0', right = '1'. Leaves get the path-so-far as their code. **No code is a prefix of another** (this is what makes the encoding decodable without delimiters — the "prefix property").

4. **Phase 4 — Encode + serialize the tree**: emit `[serialized_tree][compressed_bits]`. The tree is needed to decompress, so it goes in the header. Serialize with a simple recursive format:
   - Leaf: `'1' + 8 bits of symbol`
   - Internal: `'0' + left_subtree + right_subtree`

5. **Phase 5 — Decode**: walk the tree bit-by-bit. At each leaf, emit the symbol and reset to the root.

## The self-decompressing payload

The CMU assignment's trick is *brilliant*: produce a `.py` file that, when run, decompresses itself. The structure:

```python
#!/usr/bin/env python3
# Self-decompressing Huffman payload
import sys, base64
TREE = "..."        # serialized Huffman tree
DATA = "..."        # base64-encoded compressed bits
# ~30 lines of decoder logic
print(decode(TREE, DATA))
```

This is conceptually the same trick as a `quine` and the same idea as how `tar` self-extracts. Everything needed to reconstruct the original is in the payload.

## How to run

```bash
# Phase 1-5 implementation; tests check each phase
pytest tests/ -v

# Once tests pass, compress a real file
python -m src.encode data/english.txt > compressed.bin
python -m src.decode compressed.bin > recovered.txt
diff data/english.txt recovered.txt   # should be empty

# Print the entropy analysis — the payoff moment
python -m src.verify data/english.txt
```

`verify.py` prints something like:
```
File:                  data/english.txt
Size:                  10,431 bytes
Unique symbols:        67
Shannon entropy H:     4.512 bits/symbol  (the floor)
Huffman avg code len:  4.548 bits/symbol  (your result)
Gap from optimal:      0.036 bits/symbol  (< 1, as theory guarantees)
Compressed size:       5,925 bytes        (56.8% of original)
```

That `Gap from optimal: 0.036` is the moment everything we discussed clicks into place.

## What you'll feel when it works

- **On English text**: you'll see common letters ('e', 't', 'a') get 3-bit codes, rare ones ('z', 'q') get 12-bit codes. The code lengths *visibly* mirror `-log₂(p)`.
- **On uniform random bytes**: Huffman can't compress at all. Every code is 8 bits. This is Shannon's theorem in action — *you cannot compress maximum-entropy data*. (This is why encrypted data is incompressible!)
- **On a file with one symbol repeated**: entropy approaches 0; Huffman is forced into a 1-bit code (the minimum). This is the "degenerate distribution" edge case.

## Hints (read only if stuck)

<details>
<summary>Phase 2 hint: ties in the heap</summary>

When two nodes have equal frequency, Python's heap will try to compare the next element of the tuple. If that's a Node object, it'll error. Fix: use a counter as a tiebreaker: `heapq.heappush(heap, (freq, tiebreaker, node))`.
</details>

<details>
<summary>Phase 3 hint: edge case</summary>

What if there's only ONE unique symbol in the input? The "tree" is a single leaf, and the code is "" (empty). Special-case this: assign it code "0" so it's still decodable.
</details>

<details>
<summary>Phase 4 hint: bit packing</summary>

Python doesn't natively let you write 4.5 bytes. Accumulate a string of '0's and '1's, then pack 8 at a time into bytes with `int(chunk, 2).to_bytes(1, 'big')`. Pad the final byte with zeros and store the pad length in the header so the decoder knows where the data really ends.
</details>
