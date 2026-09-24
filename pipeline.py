"""
pipeline.py - Privacy-Preserving End-to-End Pipeline for SafeGPT

Conceptual Pipeline Flow:
User Prompt
    ↓
Hybrid PII Detection (pii_detector.py)
    ↓
Mask PII with placeholders (masker.py)
    ↓
Create PII-to-placeholder mapping (masker.py)
    ↓
Encrypt and store mapping securely using AES-256-GCM (storage/encrypted_store.py)
    ↓
Send ONLY masked prompt to local Llama 3 (llm/llm_connector.py)
    ↓
Receive LLM response containing placeholders
    ↓
Decrypt mapping when authorized
    ↓
Restore placeholders safely (demasker.py)
    ↓
Final Response to User

Security & Privacy Guarantees:
1. Raw PII is never transmitted to the LLM.
2. The PII-to-placeholder mapping is highly sensitive and is always encrypted
   with AES-256-GCM before any persistence.
3. No plaintext PII or encryption keys are written to persistent storage or exposed in logs.
4. Non-PII queries bypass mapping and encryption overhead directly.
"""

import os
from typing import Tuple, List, Dict, Any, Optional

from pii_detector import detect_pii
from masker import mask_pii, create_pii_mapping
from demasker import restore_pii
from llm.llm_connector import ask_llm
from storage.encrypted_store import (
    generate_key,
    encrypt_data,
    decrypt_data,
    save_encrypted,
    load_encrypted,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAPPING_FILE = os.path.join(BASE_DIR, "storage", "encrypted_mapping.bin")


def process_prompt(
    user_prompt: str,
    key: Optional[bytes] = None,
    persist_mapping: bool = True,
    storage_file: Optional[str] = None,
    return_full_details: bool = False,
) -> Any:
    """
    Process a user prompt through the privacy-preserving SafeGPT pipeline.

    Args:
        user_prompt: Raw user input text.
        key: Optional existing 256-bit AESGCM key. If None, a session key is generated.
        persist_mapping: Whether to write the encrypted mapping to disk.
        storage_file: Target path for the encrypted mapping file.
        return_full_details: If True, returns a comprehensive dictionary with metadata.

    Returns:
        If return_full_details is False (default):
            Tuple of (detections, masked_prompt, final_response)
        If return_full_details is True:
            Dictionary containing intermediate steps, raw response, and status flags.
    """
    if storage_file is None:
        storage_file = DEFAULT_MAPPING_FILE

    # Step 1: Hybrid PII Detection
    detections = detect_pii(user_prompt)

    # Fast path: When NO PII is detected, bypass mapping and encryption
    if not detections:
        masked_prompt = user_prompt
        # Send original prompt directly to Llama 3 since no sensitive entities were found
        llm_response = ask_llm(user_prompt)
        final_response = llm_response

        if return_full_details:
            return {
                "detections": detections,
                "masked_prompt": masked_prompt,
                "raw_llm_response": llm_response,
                "final_response": final_response,
                "has_pii": False,
                "encrypted_mapping_file": None,
            }
        return detections, masked_prompt, final_response

    # Step 2: Mask detected PII
    masked_prompt = mask_pii(user_prompt, detections)

    # Step 3: Create PII-to-placeholder mapping
    # SENSITIVITY NOTE: This mapping contains sensitive plaintext PII and must be
    # protected immediately using AES-256-GCM encryption.
    pii_mapping = create_pii_mapping(detections)

    # Step 4: Encrypt mapping using AES-256-GCM
    session_key = key if key is not None else generate_key()

    if persist_mapping:
        # Persist ONLY encrypted ciphertext to disk (never plaintext)
        save_encrypted(pii_mapping, session_key, filename=storage_file)
    else:
        encrypted_in_memory = encrypt_data(pii_mapping, session_key)

    # Step 5: Send ONLY the masked prompt to local Llama 3
    raw_llm_response = ask_llm(masked_prompt)

    # Step 6: Decrypt the mapping during authorized restoration
    if persist_mapping:
        decrypted_mapping = load_encrypted(session_key, filename=storage_file)
    else:
        decrypted_mapping = decrypt_data(encrypted_in_memory, session_key)

    # Step 7: Safely restore placeholders with original values
    final_response = restore_pii(raw_llm_response, decrypted_mapping)

    if return_full_details:
        return {
            "detections": detections,
            "masked_prompt": masked_prompt,
            "raw_llm_response": raw_llm_response,
            "final_response": final_response,
            "has_pii": True,
            "encrypted_mapping_file": storage_file if persist_mapping else None,
        }

    return detections, masked_prompt, final_response


if __name__ == "__main__":
    user_prompt = input("Enter your prompt: ")

    detections, masked_prompt, response = process_prompt(user_prompt)

    print("\n--- PII DETECTION ---")
    if detections:
        # Privacy-conscious logging: display detected labels, never raw sensitive values
        detected_categories = sorted(list(set(item["label"] for item in detections)))
        print(f"Detected PII ({len(detections)} entities): {', '.join(detected_categories)}")
    else:
        print("No PII detected.")

    print("\n--- MASKED PROMPT (sent to Llama 3) ---")
    print(masked_prompt)

    print("\n--- FINAL RESTORED RESPONSE ---")
    print(response)