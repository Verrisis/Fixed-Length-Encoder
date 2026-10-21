import time

INPUT_BUFFER_SIZE = 5 * 1024 * 1024
OUTPUT_BUFFER_LIMIT = 1 * 1024 * 1024


def calc_bits(count):
    bits = 0
    capacity = 1
    while capacity < count:
        bits += 1
        capacity *= 2
    if bits == 0:
        bits = 1
    return bits


def get_header(f):
    byte = f.read(1)
    if not byte:
        return None

    length = ord(byte)
    data = f.read(length)
    return list(data)


def decompress(input_path, output_path):
    print(f"-> Starting decompression: {input_path}")
    start_time = time.time()

    try:
        with open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
            header_dict = get_header(f_in)
            if not header_dict:
                print("Error: Damaged or empty file.")
                return

            n_bits = calc_bits(len(header_dict))
            header_size = 1 + len(header_dict)

            f_in.seek(0, 2)
            file_size = f_in.tell()
            data_size = file_size - header_size

            if data_size <= 0:
                return

            f_in.seek(header_size)

            first_byte = ord(f_in.read(1))
            padding = first_byte >> 5
            data_bits = first_byte & 0b00011111

            bit_buffer = data_bits
            bit_count = 5

            output_buffer = bytearray()
            total_bits = (data_size * 8) - padding - 3
            processed_bits = 0
            mask = (1 << n_bits) - 1

            while True:
                while bit_count >= n_bits:
                    if processed_bits >= total_bits:
                        break

                    shift = bit_count - n_bits
                    index = (bit_buffer >> shift) & mask
                    output_buffer.append(header_dict[index])

                    bit_count -= n_bits
                    processed_bits += n_bits

                    if len(output_buffer) >= OUTPUT_BUFFER_LIMIT:
                        f_out.write(output_buffer)
                        output_buffer = bytearray()

                bit_buffer &= (1 << bit_count) - 1

                if processed_bits >= total_bits:
                    break

                chunk = f_in.read(INPUT_BUFFER_SIZE)
                if not chunk:
                    break

                for byte in chunk:
                    bit_buffer = (bit_buffer << 8) | byte
                    bit_count += 8

                    while bit_count >= n_bits:
                        if processed_bits >= total_bits:
                            break

                        shift = bit_count - n_bits
                        index = (bit_buffer >> shift) & mask
                        output_buffer.append(header_dict[index])

                        if len(output_buffer) >= OUTPUT_BUFFER_LIMIT:
                            f_out.write(output_buffer)
                            output_buffer = bytearray()

                        bit_count -= n_bits
                        processed_bits += n_bits

                    bit_buffer &= (1 << bit_count) - 1

            if len(output_buffer) > 0:
                f_out.write(output_buffer)

    except FileNotFoundError:
        print("Error: No file found.")
        return

    duration = time.time() - start_time

    print("=" * 40)
    print("DECOMPRESSION SUCCESSFUL")
    print("=" * 40)
    print(f" Dictionary size : {len(header_dict)} characters")
    print(f" Length (N)      : {n_bits} bits")
    print(f" Padding (R)     : {padding} bits")
    print("-" * 40)
    print(f" Duration        : {duration:.4f} sec")
    print("=" * 40)


if __name__ == "__main__":
    decompress("compressed.bin", "decompressed.txt")
