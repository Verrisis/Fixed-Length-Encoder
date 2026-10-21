import os
import time

BUFFER_SIZE = 5 * 1024 * 1024


def get_freqs(filepath):
    counts = [0] * 256
    try:
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                for byte in chunk:
                    counts[byte] += 1
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' is missing.")
        return None

    return counts


def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def calc_bits(count):
    bits = 0
    capacity = 1
    while capacity < count:
        bits += 1
        capacity *= 2

    if bits == 0:
        bits = 1

    return bits


def create_header(sorted_chars):
    header = bytearray()
    header.append(len(sorted_chars))
    for char in sorted_chars:
        header.append(char)
    return bytes(header)


class BitWriter:
    def __init__(self, filepath, header):
        self.f = open(filepath, "wb+")
        self.f.write(header)

        self.data_start_pos = self.f.tell()
        self.buffer = 0
        self.bit_count = 3

    def write_bits(self, value, length):
        self.buffer = (self.buffer << length) | value
        self.bit_count += length

        while self.bit_count >= 8:
            shift = self.bit_count - 8
            byte_val = (self.buffer >> shift) & 0xFF
            self.f.write(bytes([byte_val]))

            self.bit_count -= 8
            self.buffer &= (1 << self.bit_count) - 1

    def flush(self):
        padding = 0
        if self.bit_count > 0:
            padding = 8 - self.bit_count
            self.buffer = self.buffer << padding
            self.f.write(bytes([self.buffer]))

        self.f.seek(self.data_start_pos)
        first_byte = self.f.read(1)

        if first_byte:
            old_val = ord(first_byte)
            new_val = (padding << 5) | old_val

            self.f.seek(self.data_start_pos)
            self.f.write(bytes([new_val]))

        self.f.close()


def compress(input_file, output_file):
    start_time = time.time()

    freqs = get_freqs(input_file)
    if freqs is None:
        return

    unique_chars = []
    for i in range(256):
        if freqs[i] > 0:
            unique_chars.append(i)

    sorted_chars = bubble_sort(unique_chars)
    n_bits = calc_bits(len(sorted_chars))

    file_size_in = os.path.getsize(input_file)
    total_stream_bits = file_size_in * n_bits + 3
    r_padding = (8 - (total_stream_bits % 8)) % 8

    dict_str = ""
    for code in sorted_chars:
        if 32 <= code <= 255:
            dict_str += chr(code)
        else:
            dict_str += "?"

    lookup = [None] * 256

    idx = 0
    for char_code in sorted_chars:
        lookup[char_code] = (idx, n_bits)
        idx += 1

    header = create_header(sorted_chars)
    writer = BitWriter(output_file, header)

    try:
        with open(input_file, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                for byte_val in chunk:
                    idx, length = lookup[byte_val]
                    writer.write_bits(idx, length)
    except FileNotFoundError:
        return

    writer.flush()

    end_time = time.time()
    duration = end_time - start_time
    file_size_out = os.path.getsize(output_file)

    print("=" * 60)
    print(f"{' ' * 20 + 'COMPRESSION REPORT'}")
    print("=" * 60)
    print(f" Dictionary           : {dict_str}")
    print("-" * 60)
    print(f" Unique symbols (X)   : {len(sorted_chars)}")
    print(f" Bits per symbol (N)  : {n_bits}")
    print(f" Padding bits (R)     : {r_padding}")
    print("-" * 60)
    print(f" Original size        : {file_size_in} bytes")
    print(f" Compressed size      : {file_size_out} bytes")
    print(f" Duration             : {duration:.3f} sec")
    print("=" * 60)


if __name__ == "__main__":
    in_file = "input.txt"
    out_file = "compressed.bin"

    if os.path.exists(in_file):
        compress(in_file, out_file)
    else:
        print(f"Error: {in_file} is missing!")
