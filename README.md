# Fixed Length Encoder

A basic file compression and decompression tool written in pure Python without external libraries. I built this as a university pet project to practice bitwise operations, binary file I/O, and custom binary headers.

## Overview

Instead of using variable-length encoding (like Huffman coding), this project implements a simpler fixed-length bit packing algorithm. Standard files store each character as an 8-bit byte, even if the file only contains a small subset of unique characters. This script counts how many unique bytes actually appear in the file and encodes each character using the minimum required number of bits ($N$).
For example, if a text file contains only 30 unique characters, each character can be encoded using 5 bits ($2^5 = 32$) instead of 8 bits, reducing the payload size by about 37.5% (excluding the header).

## How It Works

**Compression (`compressor.py`):**
* **Frequency Analysis:** The script reads the input file in 5 MB chunks and counts the occurrences of each byte value (0–255).
* **Dictionary Creation:** All unique bytes present in the file are collected and sorted in ascending order using bubble sort.
* **Bit Calculation:** The script calculates the minimum number of bits ($N$) needed to index all unique symbols.
* **Binary Header:** The output file starts with a header containing 1 byte for the dictionary length, followed by the sorted unique bytes themselves.
* **Bit Packing & Padding:** Immediately after the header, the first 3 bits are reserved to store the number of padding bits ($R$) added at the end of the file to align the stream to a full byte. The file content is then encoded by replacing each byte with its $N$-bit dictionary index.

**Decompression (`decompressor.py`):**
* **Header Parsing:** The decompressor reads the first byte to determine the dictionary size, loads the character lookup table, and recalculates the bit length ($N$).
* **Stream Decoding:** It extracts the 3-bit padding count from the first data byte, reads the remaining bitstream in 5 MB chunks, and maps each $N$-bit index back to the original byte using a 1 MB output buffer.

## Project Structure

* `compressor.py` — reads the source file, builds the header, packs the bits, and prints a compression report (dictionary, unique symbol count, bits per symbol, padding bits, file sizes, and execution time).
* `decompressor.py` — parses the compressed binary file, restores the original data, and prints a decompression summary.

## Usage
The project uses only Python standard library modules (`os` and `time`).

1. **Compress a file:**
By default, `compressor.py` looks for `input.txt` in the working directory and outputs `compressed.bin`.
```bash
python compressor.py
```
2. **Decompress a file:**
By default, `decompressor.py` reads `compressed.bin` and writes the output to `decompressed.txt`. Make sure the input filename in the `if __name__ == "__main__":` block matches your compressed file before running:
```bash
python decompressor.py
```

## Limitations

* Compression is effective only when the input file uses less than 128 unique byte values ($N \le 7$). If a file contains more than 128 unique byte values, $N$ becomes 8 bits, and the output file will be slightly larger than the original due to the header and 3-bit padding overhead.
* If a binary file contains all 256 possible byte values, the dictionary length (`256`) will exceed the 1-byte header limit (`0–255`).
