from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"
GENERATED_DIR = BASE_DIR / "generated"

# Header structure
SIGNATURE = b"IVSTEG"  # 6 bytes
VERSION = 1
HEADER_RESERVED = 0
SALT_SIZE = 16
NONCE_SIZE = 12
HEADER_SIZE = 6 + 1 + 1 + 1 + SALT_SIZE + NONCE_SIZE + 4  # 41 bytes

# Crypto
PBKDF2_ITERS = 150_000
AES_KEY_SIZE = 32  # 256-bit
