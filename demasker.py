"""
demasker.py - Safe PII Restoration / De-masking Module for SafeGPT

This module is responsible for restoring masked placeholders (e.g. [PERSON], [AADHAAR])
in LLM-generated responses using an authorized, decrypted PII mapping.

Security Guarantees:
1. Operates solely in-memory on the decrypted mapping.
2. Never logs or persists the mapping or encryption keys.
3. Enforces strict bracket matching ([LABEL]) so ordinary conversational words
   are never accidentally replaced.
4. Handles edge cases: missing placeholders, repeated placeholders, and responses
   without any placeholders.
"""

from typing import Dict, Any, Optional


def restore_pii(response_text: Optional[str], mapping: Optional[Dict[str, Any]]) -> str:
    """
    Safely replace placeholder tokens in the LLM response with original PII values.

    Args:
        response_text: The LLM response text, potentially containing placeholders like [PERSON].
        mapping: Decrypted dictionary mapping placeholders (e.g., "[PERSON]") to original PII strings.

    Returns:
        The de-masked response string with original PII values restored.
    """
    if not response_text:
        return "" if response_text is None else response_text

    if not mapping or not isinstance(mapping, dict):
        return response_text

    restored = str(response_text)

    # Sort placeholders by length descending to prevent shorter token substrings
    # from interfering with longer token matches.
    sorted_items = sorted(
        mapping.items(),
        key=lambda item: len(str(item[0])),
        reverse=True
    )

    for placeholder, original_value in sorted_items:
        if not placeholder or original_value is None:
            continue

        token = str(placeholder).strip()

        # Enforce brackets around the placeholder token to prevent accidental
        # substitution of ordinary dictionary words in the response text.
        if not (token.startswith("[") and token.endswith("]")):
            token = f"[{token}]"

        replacement = str(original_value)

        # Replace all occurrences of this specific placeholder token
        restored = restored.replace(token, replacement)

    return restored


# Alias for semantic clarity
demask_response = restore_pii


if __name__ == "__main__":
    # Internal module sanity check
    sample_response = "Hello [PERSON], your Aadhaar [AADHAAR] has been verified. Have a good day, [PERSON]."
    sample_mapping = {
        "[PERSON]": "Ananya Iyer",
        "[AADHAAR]": "2222 3333 4444"
    }

    result = restore_pii(sample_response, sample_mapping)
    print("Sanity test demasking:")
    print("Input :", sample_response)
    print("Output:", result)
