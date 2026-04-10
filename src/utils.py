from __future__ import annotations

import io
import numpy as np
from PIL import Image


def open_image(uploaded_file) -> Image.Image:
    return Image.open(uploaded_file).convert("RGB")


def image_to_png_bytes(img: Image.Image) -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def png_bytes_to_image(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")


def create_diff_image(img1: Image.Image, img2: Image.Image, boost: int = 12) -> Image.Image:
    a = np.array(img1.convert("RGB"), dtype=np.uint8)
    b = np.array(img2.convert("RGB"), dtype=np.uint8)

    diff = np.abs(a.astype(np.int16) - b.astype(np.int16)) * boost
    diff = np.clip(diff, 0, 255).astype(np.uint8)

    return Image.fromarray(diff)