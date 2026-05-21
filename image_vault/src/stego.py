import numpy as np
from PIL import Image
from .config import SIGNATURE, VERSION, HEADER_RESERVED, SALT_SIZE, NONCE_SIZE, HEADER_SIZE
from .utils import array_from_image, image_from_array, bytes_to_bits, bits_to_bytes, pil_to_png_bytes
from .security import encrypt_bytes, decrypt_bytes
import time


def _build_header(encrypted: bool, salt: bytes, nonce: bytes, payload_len: int) -> bytes:
    flags = 1 if encrypted else 0
    parts = [
        SIGNATURE,
        bytes([VERSION]),
        bytes([flags]),
        bytes([HEADER_RESERVED]),
    ]
    # fixed sizes: salt, nonce
    if salt is None:
        parts.append(bytes(SALT_SIZE))
    else:
        parts.append(salt)
    if nonce is None:
        parts.append(bytes(NONCE_SIZE))
    else:
        parts.append(nonce)
    parts.append(payload_len.to_bytes(4, "big"))
    return b"".join(parts)


def embed_bytes_into_image(cover_img: Image.Image, payload: bytes) -> tuple:
    """
    Embed payload (header+data) into cover_img using 2-bit LSB across RGB channels.
    Returns (encoded_image_pil, diff_map_array)
    """
    cover = cover_img.convert("RGBA")
    arr = array_from_image(cover).copy()
    h, w, c = arr.shape
    # use only RGB channels for embedding
    carrier = arr[:, :, :3].flatten()
    total_capacity_bits = carrier.size * 2
    payload_bits = bytes_to_bits(payload)
    if len(payload_bits) > total_capacity_bits:
        raise ValueError("Payload too large for given cover image")
    # embed 2 bits per carrier byte
    # pad payload_bits to even length for mapping
    if len(payload_bits) % 2 != 0:
        payload_bits.append(0)
    # iterate two bits at a time
    for i in range(0, len(payload_bits), 2):
        two_bits = (payload_bits[i] << 1) | payload_bits[i+1]
        idx = i // 2
        carrier[idx] = (carrier[idx] & ~0b11) | two_bits
    # write back
    arr_emb = arr.copy()
    arr_emb[:, :, :3] = carrier.reshape((h, w, 3))
    encoded = image_from_array(arr_emb)
    # difference map
    diff = np.abs(array_from_image(cover)[:, :, :3].astype(int) - arr_emb[:, :, :3].astype(int)).astype(np.uint8)
    return encoded, diff


def extract_bytes_from_image(encoded_img: Image.Image) -> tuple:
    """
    Extract embedded bytes from encoded image.
    Returns (header_bytes, payload_bytes, decode_time_seconds)
    """
    start = time.time()
    arr = array_from_image(encoded_img.convert("RGBA"))
    carrier = arr[:, :, :3].flatten()
    # extract 2 LSBs from each carrier byte
    bits = []
    for b in carrier:
        two = b & 0b11
        bits.append((two >> 1) & 1)
        bits.append(two & 1)
    # first HEADER_SIZE bytes are header
    header_bits_len = HEADER_SIZE * 8
    header_bits = bits[:header_bits_len]
    header = bits_to_bytes(header_bits)
    # parse header
    sig = header[0:6]
    if sig != SIGNATURE:
        raise ValueError("Invalid signature — not an Image Vault encoded image")
    version = header[6]
    flags = header[7]
    # reserved = header[8]
    salt = header[9:9+SALT_SIZE]
    nonce = header[9+SALT_SIZE:9+SALT_SIZE+NONCE_SIZE]
    payload_len = int.from_bytes(header[-4:], "big")
    # extract payload bits
    payload_bits = bits[header_bits_len:header_bits_len + payload_len * 8]
    payload = bits_to_bytes(payload_bits)
    end = time.time()
    return header, payload, end - start


def prepare_payload(secret_img: Image.Image, password: str = None) -> tuple:
    secret_bytes = pil_to_png_bytes(secret_img)
    if password:
        salt, nonce, ct = encrypt_bytes(password, secret_bytes)
        header = _build_header(True, salt, nonce, len(ct))
        payload = ct
    else:
        header = _build_header(False, None, None, len(secret_bytes))
        payload = secret_bytes
    return header + payload
