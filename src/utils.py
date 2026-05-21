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


def calculate_psnr(img1: Image.Image, img2: Image.Image) -> float:
    a = np.array(img1.convert("RGB"), dtype=np.float32)
    b = np.array(img2.convert("RGB"), dtype=np.float32)

    if a.shape != b.shape:
        raise ValueError("Images must have the same dimensions to compute PSNR.")

    mse = np.mean((a - b) ** 2)
    if mse == 0:
        return float("inf")

    max_i = 255.0
    return 20 * np.log10(max_i) - 10 * np.log10(mse)


def fit_image_to_capacity(
    img: Image.Image,
    capacity: int,
    max_steps: int = 12,
    min_scale: float = 0.1,
) -> tuple[Image.Image, bytes, bool]:
    """Resize image until PNG bytes fit within capacity."""
    resized = False
    current = img
    png_bytes = image_to_png_bytes(current)

    if len(png_bytes) <= capacity:
        return current, png_bytes, resized

    resized = True
    for _ in range(max_steps):
        scale = (capacity / max(1, len(png_bytes))) ** 0.5
        scale = min(0.95, max(min_scale, scale))
        new_w = max(1, int(current.width * scale))
        new_h = max(1, int(current.height * scale))

        if new_w == current.width and new_h == current.height:
            new_w = max(1, int(current.width * min_scale))
            new_h = max(1, int(current.height * min_scale))

        current = current.resize((new_w, new_h), Image.LANCZOS)
        png_bytes = image_to_png_bytes(current)

        if len(png_bytes) <= capacity:
            return current, png_bytes, resized

    return current, png_bytes, resized