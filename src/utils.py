from __future__ import annotations

import io
from typing import Tuple

import numpy as np
from PIL import Image, ImageOps


def open_image(uploaded_file) -> Image.Image:
    return Image.open(uploaded_file).convert("RGB")


def fit_secret_to_cover(secret_img: Image.Image, cover_img: Image.Image) -> Image.Image:
    return secret_img.resize(cover_img.size)


def pil_to_array(img: Image.Image) -> np.ndarray:
    return np.array(img, dtype=np.uint8)


def array_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr.astype(np.uint8))


def image_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_diff_image(img1: Image.Image, img2: Image.Image, boost: int = 12) -> Image.Image:
    a = pil_to_array(img1)
    b = pil_to_array(img2)
    diff = np.abs(a.astype(np.int16) - b.astype(np.int16)) * boost
    diff = np.clip(diff, 0, 255).astype(np.uint8)
    return array_to_pil(diff)


def estimate_capacity(cover_img: Image.Image, bits_used: int = 4) -> Tuple[int, int]:
    width, height = cover_img.size
    total_channels = width * height * 3
    total_bits = total_channels * bits_used
    total_bytes = total_bits // 8
    total_kb = total_bytes // 1024
    return total_bytes, total_kb


def add_checker_background(img: Image.Image, tile: int = 18) -> Image.Image:
    w, h = img.size
    bg = Image.new("RGB", (w, h), (240, 240, 240))
    px = bg.load()
    for y in range(h):
        for x in range(w):
            if ((x // tile) + (y // tile)) % 2 == 0:
                px[x, y] = (238, 238, 238)
            else:
                px[x, y] = (220, 220, 220)
    bg.paste(img, (0, 0))
    return bg


def safe_text_preview(text: str, limit: int = 120) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "..."