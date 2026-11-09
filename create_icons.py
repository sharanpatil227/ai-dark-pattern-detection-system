"""
Generate valid PNG icons for DarkGuard Chrome Extension using Python's standard library.
"""

import os
import zlib
import struct


def create_png(width, height, color_rgb=(79, 70, 229)):
    """Generate raw binary PNG data without external libraries."""
    # PNG signature
    png_signature = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data))
    ihdr_chunk = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + ihdr_crc

    # Image scanlines (filter type 0: None)
    raw_data = bytearray()
    r, g, b = color_rgb

    for y in range(height):
        raw_data.append(0)  # filter type
        for x in range(width):
            # Draw a simple rounded shield pattern
            # Center coordinates
            cx, cy = width / 2.0, height / 2.0
            dx, dy = (x - cx) / (width / 2.0), (y - cy) / (height / 2.0)
            dist = dx * dx + dy * dy

            if dist <= 0.85:
                # Inside shield
                raw_data.extend([r, g, b])
            else:
                # Border / background
                raw_data.extend([240, 240, 250])

    # IDAT chunk
    compressed_data = zlib.compress(bytes(raw_data))
    idat_crc = struct.pack(">I", zlib.crc32(b"IDAT" + compressed_data))
    idat_chunk = struct.pack(">I", len(compressed_data)) + b"IDAT" + compressed_data + idat_crc

    # IEND chunk
    iend_data = b""
    iend_crc = struct.pack(">I", zlib.crc32(b"IEND" + iend_data))
    iend_chunk = struct.pack(">I", len(iend_data)) + b"IEND" + iend_data + iend_crc

    return png_signature + ihdr_chunk + idat_chunk + iend_chunk


def main():
    icons_dir = os.path.join(os.path.dirname(__file__), "extension", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    sizes = [16, 32, 48, 128]
    for size in sizes:
        png_bytes = create_png(size, size)
        out_path = os.path.join(icons_dir, f"icon{size}.png")
        with open(out_path, "wb") as f:
            f.write(png_bytes)
        print(f"Generated {out_path} ({len(png_bytes)} bytes)")


if __name__ == "__main__":
    main()

