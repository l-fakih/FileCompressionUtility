"""
Demo: damage a compressed file on purpose and check that we notice.

For each algorithm it compresses a sample file, flips ONE bit somewhere in the
compressed data, then tries to decompress. A good run says "detected" every time.

Usage:
    python test_errors.py
"""

import os
import random
import tempfile

import huffman
import rle

ALGORITHMS = {
    "Huffman": (huffman.compress, huffman.decompress),
    "RLE": (rle.compress, rle.decompress),
}
TRIALS = 20  # how many random bit flips to try per algorithm


def flip_one_bit(path, position):
    """Flip a single bit of the byte at 'position' (like a disk or network error)."""
    with open(path, "rb") as f:
        data = bytearray(f.read())
    data[position] ^= 1 << random.randrange(8)  # XOR with e.g. 00000100 flips that bit
    with open(path, "wb") as f:
        f.write(data)


def main():
    random.seed(2)
    sample = b"the quick brown fox jumps over the lazy dog. " * 200 + b"A" * 300

    with tempfile.TemporaryDirectory() as folder:
        original = os.path.join(folder, "original.txt")
        packed = os.path.join(folder, "packed.tmp")
        restored = os.path.join(folder, "restored.tmp")
        with open(original, "wb") as f:
            f.write(sample)

        for name, (compress, decompress) in ALGORITHMS.items():
            detected = 0
            last_message = "(none)"
            for _ in range(TRIALS):
                compress(original, packed)
                size = os.path.getsize(packed)
                flip_one_bit(packed, random.randrange(3, size))  # skip the 3-byte "HUF"/"RLE" tag
                try:
                    decompress(packed, restored)
                    print(f"{name}: damage NOT detected")
                except ValueError as error:
                    detected += 1
                    last_message = str(error)
            print(f"{name}: detected {detected} of {TRIALS} single-bit errors")
            print(f"  example message: {last_message}")


if __name__ == "__main__":
    main()
