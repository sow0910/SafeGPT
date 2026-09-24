"""
encrypted_store.py - AES-256-GCM Encrypted Storage Module for SafeGPT

Provides authenticated encryption (AEAD) with AES-256-GCM to securely protect
the sensitive PII-to-placeholder mapping before persistent storage.

KEY MANAGEMENT NOTE:
The current academic prototype dynamically generates 256-bit keys during execution
or receives them via function arguments. Persistent secure key management
(e.g., enterprise KMS, OS Keychains, or HSMs) is outside the current prototype
scope and is documented as future work. No hardcoded keys exist in this system.
"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Generate a new 256-bit encryption key
def generate_key():
    return AESGCM.generate_key(bit_length=256)


# Encrypt data
def encrypt_data(data, key):
    aesgcm = AESGCM(key)

    # Convert dictionary to JSON bytes
    plaintext = json.dumps(data).encode("utf-8")

    # Generate a random nonce
    nonce = os.urandom(12)

    # Encrypt
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    # Store nonce + encrypted data together
    encrypted_data = nonce + ciphertext

    return base64.b64encode(encrypted_data).decode("utf-8")


# Decrypt data
def decrypt_data(encrypted_data, key):
    aesgcm = AESGCM(key)

    # Convert from Base64
    encrypted_bytes = base64.b64decode(encrypted_data)

    # Separate nonce and ciphertext
    nonce = encrypted_bytes[:12]
    ciphertext = encrypted_bytes[12:]

    # Decrypt
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    return json.loads(plaintext.decode("utf-8"))


# Save encrypted data to a file
def save_encrypted(data, key, filename="storage/encrypted_data.bin"):
    encrypted_data = encrypt_data(data, key)

    with open(filename, "w") as file:
        file.write(encrypted_data)


# Load and decrypt data from a file
def load_encrypted(key, filename="storage/encrypted_data.bin"):
    with open(filename, "r") as file:
        encrypted_data = file.read()

    return decrypt_data(encrypted_data, key)