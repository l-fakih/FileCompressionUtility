"""
Huffman file compressor / decompressor.

Usage:
    python huffman.py compress   input.txt   output.huf
    python huffman.py decompress output.huf  restored.txt
"""

import heapq
import sys

MAGIC = b"HUF"  # first 3 bytes of every compressed file, so we can recognise it


# ---------------------------------------------------------------------------
# STEP 1: Count how often each byte appears
# ---------------------------------------------------------------------------
def count_frequencies(data):
    """Return a dict {byte_value: count}. Example for b"aab": {97: 2, 98: 1}"""
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    return freq


# ---------------------------------------------------------------------------
# STEP 2: Build the Huffman tree
# ---------------------------------------------------------------------------
class Node:
    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq      # how many times this symbol (or subtree) appears
        self.symbol = symbol  # the byte value; None for internal nodes
        self.left = left      # child on the "0" side
        self.right = right    # child on the "1" side

    def is_leaf(self):
        return self.symbol is not None


def build_tree(freq):
    """
    Repeatedly take the TWO least frequent nodes and join them under a new
    parent, until only one node (the root) is left.
    A min-heap (priority queue) gives us the smallest node quickly.
    """
    heap = []
    order = 0  # tie-breaker so equal frequencies always come out in the same order
    for symbol in sorted(freq):
        heapq.heappush(heap, (freq[symbol], order, Node(freq[symbol], symbol)))
        order += 1

    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)   # smallest
        f2, _, right = heapq.heappop(heap)  # second smallest
        parent = Node(f1 + f2, left=left, right=right)
        heapq.heappush(heap, (parent.freq, order, parent))
        order += 1

    return heap[0][2]  # the root


# ---------------------------------------------------------------------------
# STEP 3: Walk the tree to give each byte its code (left = 0, right = 1)
# ---------------------------------------------------------------------------
def build_codes(node, prefix="", codes=None):
    if codes is None:
        codes = {}
    if node.is_leaf():
        # Special case: a file with only one distinct byte, e.g. "aaaa".
        codes[node.symbol] = prefix or "0"
    else:
        build_codes(node.left, prefix + "0", codes)
        build_codes(node.right, prefix + "1", codes)
    return codes


# ---------------------------------------------------------------------------
# STEP 4: Bit helpers (turn a string of '0'/'1' into real bytes and back)
# ---------------------------------------------------------------------------
def bits_to_bytes(bits):
    """'0100000101' -> bytes. Pads the end with 0s to fill the last byte."""
    padding = (8 - len(bits) % 8) % 8
    bits += "0" * padding
    out = bytearray()
    for i in range(0, len(bits), 8):
        out.append(int(bits[i:i + 8], 2))  # '01000001' -> 65
    return bytes(out), padding


def bytes_to_bits(data):
    """bytes -> '0100000101...' (8 characters per byte)."""
    return "".join(format(byte, "08b") for byte in data)  # 65 -> '01000001'


# ---------------------------------------------------------------------------
# COMPRESS
# ---------------------------------------------------------------------------
def compress(input_path, output_path):
    with open(input_path, "rb") as f:  # "rb" = read raw bytes, works for any file
        data = f.read()

    freq = count_frequencies(data)

    with open(output_path, "wb") as out:
        out.write(MAGIC)
        # Header: the frequency table, so the decompressor can rebuild the same tree.
        out.write(len(freq).to_bytes(2, "big"))          # number of distinct bytes (0-256)
        for symbol in sorted(freq):
            out.write(bytes([symbol]))                    # 1 byte: the symbol
            out.write(freq[symbol].to_bytes(4, "big"))    # 4 bytes: its count

        if not data:  # empty file: header only
            out.write(bytes([0]))
            return

        codes = build_codes(build_tree(freq))
        bits = "".join(codes[byte] for byte in data)
        packed, padding = bits_to_bytes(bits)

        out.write(bytes([padding]))  # how many fake 0s we added at the end
        out.write(packed)


# ---------------------------------------------------------------------------
# DECOMPRESS
# ---------------------------------------------------------------------------
def decompress(input_path, output_path):
    with open(input_path, "rb") as f:
        data = f.read()

    if data[:3] != MAGIC:
        raise ValueError("Not a .huf file")
    pos = 3

    # Read the frequency table back.
    count = int.from_bytes(data[pos:pos + 2], "big")
    pos += 2
    freq = {}
    for _ in range(count):
        symbol = data[pos]
        freq[symbol] = int.from_bytes(data[pos + 1:pos + 5], "big")
        pos += 5

    padding = data[pos]
    pos += 1

    if not freq:  # it was an empty file
        open(output_path, "wb").close()
        return

    root = build_tree(freq)  # same table + same rules = exactly the same tree
    total = sum(freq.values())  # how many bytes the original file had

    bits = bytes_to_bits(data[pos:])
    if padding:
        bits = bits[:-padding]

    out = bytearray()
    if root.is_leaf():  # only one distinct byte in the original file
        out.extend([root.symbol] * total)
    else:
        node = root
        for bit in bits:
            node = node.left if bit == "0" else node.right  # walk down the tree
            if node.is_leaf():                              # reached a symbol
                out.append(node.symbol)
                node = root                                 # start again from the top

    with open(output_path, "wb") as f:
        f.write(out)


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os

    if len(sys.argv) != 4 or sys.argv[1] not in ("compress", "decompress"):
        print(__doc__)
        sys.exit(1)

    mode, src, dst = sys.argv[1:]
    if mode == "compress":
        compress(src, dst)
    else:
        decompress(src, dst)

    before, after = os.path.getsize(src), os.path.getsize(dst)
    print(f"{mode}: {before} bytes -> {after} bytes")
    if mode == "compress" and before:
        print(f"Compressed size is {after / before:.1%} of the original")
