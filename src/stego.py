from __future__ import annotations

import struct
import numpy as np
from PIL import Image


class StegoError(Exception):
    pass


HEADER_SIZE = 4  # store payload length in 4 bytes


def _bytes_to_bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def _bits_to_bytes(bits: np.ndarray) -> bytes:
    if len(bits) % 8 != 0:
        raise StegoError("Bit length must be a multiple of 8.")
    return np.packbits(bits).tobytes()


def capacity_bytes(cover_img: Image.Image) -> int:
    arr = np.array(cover_img.convert("RGB"), dtype=np.uint8)
    total_channels = arr.size
    total_bits = total_channels
    total_bytes = total_bits // 8
    usable = total_bytes - HEADER_SIZE
    return max(0, usable)


def encode_image_bytes(cover_img: Image.Image, secret_bytes: bytes) -> Image.Image:
    cover = cover_img.convert("RGB")
    arr = np.array(cover, dtype=np.uint8)
    flat = arr.reshape(-1)

    payload = struct.pack(">I", len(secret_bytes)) + secret_bytes
    payload_bits = _bytes_to_bits(payload)

    if len(payload_bits) > len(flat):
        raise StegoError(
            "Secret image is too large for this cover image. Use a larger cover image."
        )

    encoded_flat = flat.copy()
    encoded_flat[:len(payload_bits)] = (encoded_flat[:len(payload_bits)] & 0xFE) | payload_bits

    encoded_arr = encoded_flat.reshape(arr.shape)
    return Image.fromarray(encoded_arr.astype(np.uint8), mode="RGB")


def decode_image_bytes(encoded_img: Image.Image) -> bytes:
    encoded = encoded_img.convert("RGB")
    arr = np.array(encoded, dtype=np.uint8)
    flat = arr.reshape(-1)

    bits = flat & 1

    header_bits = bits[:HEADER_SIZE * 8]
    payload_length = struct.unpack(">I", _bits_to_bytes(header_bits))[0]

    total_bits_needed = (HEADER_SIZE + payload_length) * 8

    if total_bits_needed > len(bits):
        raise StegoError("Encoded image does not contain a valid hidden payload.")

    payload_bits = bits[:total_bits_needed]
    payload_bytes = _bits_to_bytes(payload_bits)

    return payload_bytes[HEADER_SIZE:]