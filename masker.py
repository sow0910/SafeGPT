def mask_pii(text, detections):
    """
    Replace detected PII with its label.
    """

    masked_text = text

    # Process from the end of the text to the beginning
    for item in reversed(detections):

        start = item["start"]
        end = item["end"]
        label = item["label"]

        masked_text = (
            masked_text[:start]
            + f"[{label}]"
            + masked_text[end:]
        )

    return masked_text


def create_pii_mapping(detections):
    """
    Generate a placeholder-to-PII dictionary from detection metadata.

    SECURITY SENSITIVITY:
    This mapping contains raw, sensitive PII extracted from user input.
    - NEVER log, serialize in plaintext, or expose this mapping.
    - It must be encrypted with AES-256-GCM immediately before persistent storage.
    - Used strictly in memory during authorized restoration/de-masking.

    Example output:
    {
        "[PERSON]": "Ananya Iyer",
        "[AADHAAR]": "2222 3333 4444"
    }
    """
    mapping = {}

    for item in detections:
        placeholder = f"[{item['label']}]"
        # Preserve first occurrence mapping if duplicate labels exist
        if placeholder not in mapping:
            mapping[placeholder] = item["text"]

    return mapping


def mask_and_map_pii(text, detections):
    """
    Convenience function to perform both masking and mapping extraction.

    Returns:
        tuple: (masked_text, pii_mapping)
    """
    masked_text = mask_pii(text, detections)
    mapping = create_pii_mapping(detections)
    return masked_text, mapping


if __name__ == "__main__":

    from pii_detector import detect_pii

    text = """
    My Aadhaar number is 2345 6789 0123.
    My PAN is ABCDE1234F.
    My phone number is +91 98765 43210.
    My email is sneha@example.com.
    """

    detections = detect_pii(text)

    print("Detected labels:", [item["label"] for item in detections])
    masked_text = mask_pii(text, detections)
    print("Masked text:")
    print(masked_text)