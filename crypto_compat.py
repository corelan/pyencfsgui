"""Compatibility layer for PyCrypto/PyCryptodome imports."""

CRYPTO_BACKEND = ""

try:
    from Crypto import Random  # type: ignore
    from Crypto.Cipher import AES  # type: ignore

    CRYPTO_BACKEND = "Crypto"
except ImportError:
    from Cryptodome import Random  # type: ignore
    from Cryptodome.Cipher import AES  # type: ignore

    CRYPTO_BACKEND = "Cryptodome"
