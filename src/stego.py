from __future__ import annotations

import numpy as np
from PIL import Image

from src.utils import array_to_pil, fit_secret_to_cover, pil_to_array


class StegoError(Exception):
    pass


# 4-bit image-in-image steganography
# encoded = upper 4 bits of cover + upper 4 bits of secret
# decoded = lower 4 bits shifted back

def encode_image(cover_img: Image.Image, secret_img: Image.Image) -> Image.Image:
    cover_img = cover_img.convert("RGB")
    secret_img = fit_secret_to_cover(secret_img.convert("RGB"), cover_img)

    cover = pil_to_array(cover_img)
    secret = pil_to_array(secret_img)

    encoded = (cover & 0xF0) | (secret >> 4)
    return array_to_pil(encoded)



def decode_image(encoded_img: Image.Image) -> Image.Image:
    encoded = pil_to_array(encoded_img.convert("RGB"))
    decoded = (encoded & 0x0F) << 4
    return array_to_pil(decoded)