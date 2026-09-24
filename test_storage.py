from storage.encrypted_store import generate_key, save_encrypted, load_encrypted


data = {
    "[PERSON]": "Ananya Iyer",
    "[AADHAAR]": "2222 3333 4444"
}

# Generate AES-256 key
key = generate_key()

# Save encrypted data
save_encrypted(data, key)

print("\n✅ Data encrypted and saved.")

# Load and decrypt
decrypted = load_encrypted(key)

print("\n========== DECRYPTION CHECK ==========")
print("Decrypted keys:", sorted(decrypted.keys()) if isinstance(decrypted, dict) else type(decrypted).__name__)
print("Round-trip match:", decrypted == data)