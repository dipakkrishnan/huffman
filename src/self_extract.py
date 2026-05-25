"""
Bonus: produce a self-decompressing .py file from any input.

The output is a runnable Python script that contains:
    - The compressed payload (base64-encoded)
    - A minimal Huffman decoder
    - A line that decodes the payload and writes it to stdout

It's the same conceptual move as:
    - tar self-extracting archives
    - quines (programs that print their own source)
    - bootloaders that contain the code to load themselves

Run after implementing encode/decode:
    python -m src.self_extract data/english.txt > extract.py
    python extract.py > recovered.txt
    diff data/english.txt recovered.txt   # should be empty
"""
from __future__ import annotations
import base64
import sys
from .encode import encode


TEMPLATE = '''\
#!/usr/bin/env python3
"""Self-decompressing Huffman payload. Run me: `python {this_file}`."""
import base64, sys

PAYLOAD = """{payload_b64}"""

def decode(data):
    if len(data) < 8: return b""
    tlen = int.from_bytes(data[0:4], "big")
    if tlen == 0: return b""
    tbytes = (tlen + 7) // 8
    tb = data[4:4+tbytes]
    tbits = "".join(f"{{b:08b}}" for b in tb)[:tlen]

    def deser(bits, pos):
        flag = bits[pos]; pos += 1
        if flag == "1":
            return {{"sym": int(bits[pos:pos+8], 2), "left": None, "right": None}}, pos+8
        L, pos = deser(bits, pos)
        R, pos = deser(bits, pos)
        return {{"sym": None, "left": L, "right": R}}, pos

    root, _ = deser(tbits, 0)
    off = 4 + tbytes
    plen = int.from_bytes(data[off:off+4], "big")
    pbytes = (plen + 7) // 8
    pb = data[off+4:off+4+pbytes]
    pbits = "".join(f"{{b:08b}}" for b in pb)[:plen]

    out = bytearray()
    if root["left"] is None:   # single-leaf tree
        for _ in range(plen): out.append(root["sym"])
        return bytes(out)
    node = root
    for bit in pbits:
        node = node["left"] if bit == "0" else node["right"]
        if node["left"] is None:
            out.append(node["sym"]); node = root
    return bytes(out)

sys.stdout.buffer.write(decode(base64.b64decode(PAYLOAD)))
'''


def build_self_extracting(data: bytes, this_file: str = "extract.py") -> str:
    """Return Python source that, when run, prints `data` to stdout."""
    compressed = encode(data)
    payload_b64 = base64.b64encode(compressed).decode("ascii")
    # Wrap base64 to 76 chars per line for readability.
    wrapped = "\\\n".join(
        payload_b64[i:i + 76] for i in range(0, len(payload_b64), 76)
    )
    return TEMPLATE.format(this_file=this_file, payload_b64=wrapped)


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python -m src.self_extract <file> > extract.py",
              file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    print(build_self_extracting(data, "extract.py"))


if __name__ == "__main__":
    main()
