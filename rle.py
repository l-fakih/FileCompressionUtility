"""
Run-Length Encoding (RLE) file compressor / decompressor.

Idea: replace a run of the same byte with (how many times, which byte).
    b"aaaaabbbc"  ->  (5,'a') (3,'b') (1,'c')  ->  6 bytes instead of 9

Usage:
    python rle.py compress   input.txt  output.rle
    python rle.py decompress output.rle restored.txt
"""

import sys

MAGIC = b"RLE"  # first 3 bytes of every RLE file, so we can recognise it
MAX_RUN = 255   # the count is stored in 1 byte, so a run can be at most 255 long


def rle_encode(data):
    """Turn bytes into pairs: [count, byte, count, byte, ...]."""
    out = bytearray()
    i = 0
    while i < len(data):
        current = data[i]
        run = 1
        # Keep going while the next byte is the same (and the run still fits in 1 byte).
        while i + run < len(data) and data[i + run] == current and run < MAX_RUN:
            run += 1
        out.append(run)      # 1 byte: how many times
        out.append(current)  # 1 byte: which byte
        i += run
    return bytes(out)


def rle_decode(data):
    """Turn pairs [count, byte, ...] back into the original bytes."""
    if len(data) % 2 != 0:
        raise ValueError("Corrupted RLE data: odd number of bytes")
    out = bytearray()
    for i in range(0, len(data), 2):
        count, value = data[i], data[i + 1]
        out.extend([value] * count)  # write the byte 'count' times
    return bytes(out)


def compress(input_path, output_path):
    with open(input_path, "rb") as f:
        data = f.read()
    with open(output_path, "wb") as out:
        out.write(MAGIC)
        out.write(rle_encode(data))


def decompress(input_path, output_path):
    with open(input_path, "rb") as f:
        data = f.read()
    if data[:3] != MAGIC:
        raise ValueError("Not a .rle file")
    with open(output_path, "wb") as out:
        out.write(rle_decode(data[3:]))


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
