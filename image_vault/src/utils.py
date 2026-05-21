import io
from PIL import Image
import numpy as np


def pil_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def png_bytes_to_pil(b: bytes) -> Image.Image:
    buf = io.BytesIO(b)
    img = Image.open(buf).convert("RGBA")
    return img


def bytes_to_bits(b: bytes) -> list:
    bits = []
    for byte in b:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_bytes(bits: list) -> bytes:
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        chunk = bits[i:i+8]
        for bit in chunk:
            byte = (byte << 1) | bit
        # pad if needed
        if len(chunk) < 8:
            byte <<= (8 - len(chunk))
        out.append(byte)
    return bytes(out)


def ensure_rgba(img: Image.Image) -> Image.Image:
    return img.convert("RGBA")


def array_from_image(img: Image.Image) -> np.ndarray:
    return np.array(ensure_rgba(img))


def image_from_array(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr)
