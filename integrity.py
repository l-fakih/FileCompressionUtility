"""
Error detection: a parity byte and a checksum.

When we compress, we calculate both values from the ORIGINAL data and store
them in the compressed file (5 bytes). When we decompress, we calculate them
again from the RESTORED data. If they don't match, the file was damaged.

1. Parity byte (8 parity bits, one per bit position)
   XOR all bytes together. Each bit of the result says whether that bit
   position had an odd (1) or even (0) number of 1s across the whole file.
       01000001  'A'
     ^ 01000010  'B'
     = 00000011  parity byte
   Flip ANY single bit in the data and that column's parity changes -> detected.
   Weakness: two flips in the same column cancel out.

2. Checksum (sum of all bytes, kept to 32 bits)
   Catches many errors the parity byte misses, e.g. two flips in the same column.
   Weakness: swapping two bytes gives the same sum.

Using both together catches far more errors than either one alone.
"""

CHECK_SIZE = 5  # 1 byte parity + 4 bytes checksum


def parity_byte(data):
    parity = 0
    for byte in data:
        parity ^= byte  # ^ is XOR: 1 if the two bits differ, 0 if they are the same
    return parity


def checksum(data):
    return sum(data) % 2**32  # keep it small enough to fit in 4 bytes


def make_check(data):
    """The 5 bytes we store in the compressed file."""
    return bytes([parity_byte(data)]) + checksum(data).to_bytes(4, "big")


def verify(restored, stored_check):
    """Raise an error if the restored data doesn't match the stored check values."""
    stored_parity = stored_check[0]
    stored_sum = int.from_bytes(stored_check[1:5], "big")

    problems = []
    if parity_byte(restored) != stored_parity:
        problems.append("parity byte does not match")
    if checksum(restored) != stored_sum:
        problems.append("checksum does not match")
    if problems:
        raise ValueError("File is corrupted: " + " and ".join(problems))
