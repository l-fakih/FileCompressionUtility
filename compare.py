"""
Compare Huffman and RLE: compressed size, ratio and time.

Usage:
    python compare.py                    # runs on 4 built-in demo files
    python compare.py file1 file2 ...    # runs on your own files
"""

import os
import random
import sys
import tempfile
import time

import huffman
import rle

ALGORITHMS = {
    "Huffman": (huffman.compress, huffman.decompress),
    "RLE": (rle.compress, rle.decompress),
}


def make_demo_files(folder):
    """Create 4 small files that each show a different behaviour."""
    random.seed(1)  # same "random" file every run, so results are repeatable
    samples = {
        # Normal text: many different letters, few long runs -> Huffman wins.
        "text.txt": b"the quick brown fox jumps over the lazy dog. " * 500,
        # Long runs of the same byte -> RLE wins.
        "runs.txt": (b"A" * 200 + b"B" * 150 + b"C" * 100 + b"\n") * 50,
        # Like a simple image: rows of repeated "pixels".
        "image_like.bin": bytes([0] * 300 + [255] * 100 + [128] * 112) * 40,
        # Random bytes: no patterns at all -> both make the file bigger.
        "random.bin": bytes(random.randrange(256) for _ in range(20000)),
    }
    paths = []
    for name, data in samples.items():
        path = os.path.join(folder, name)
        with open(path, "wb") as f:
            f.write(data)
        paths.append(path)
    return paths


def run_one(path, compress, decompress, folder):
    """Compress then decompress one file. Returns size, times and whether it matched."""
    packed = os.path.join(folder, "packed.tmp")
    restored = os.path.join(folder, "restored.tmp")

    start = time.perf_counter()
    compress(path, packed)
    compress_time = time.perf_counter() - start

    start = time.perf_counter()
    decompress(packed, restored)
    decompress_time = time.perf_counter() - start

    with open(path, "rb") as a, open(restored, "rb") as b:
        matched = a.read() == b.read()

    return os.path.getsize(packed), compress_time, decompress_time, matched


def main():
    with tempfile.TemporaryDirectory() as folder:
        files = sys.argv[1:] or make_demo_files(folder)

        header = (f"{'File':<16}{'Algorithm':<10}{'Original':>10}{'Compressed':>12}"
                  f"{'Ratio':>8}{'Compress':>11}{'Decompress':>12}  OK")
        print(header)
        print("-" * len(header))

        for path in files:
            original = os.path.getsize(path)
            for name, (compress, decompress) in ALGORITHMS.items():
                size, c_time, d_time, ok = run_one(path, compress, decompress, folder)
                ratio = f"{size / original:.0%}" if original else "-"
                print(f"{os.path.basename(path)[:15]:<16}{name:<10}{original:>10}{size:>12}{ratio:>8}"
                      f"{c_time * 1000:>9.1f}ms{d_time * 1000:>10.1f}ms  {'yes' if ok else 'NO'}")
            print()

    print("Ratio = compressed size / original size (lower is better; over 100% means the file grew).")


if __name__ == "__main__":
    main()
