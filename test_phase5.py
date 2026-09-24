"""
test_phase5.py - Verification Suite for Phase 5 (Secure PII Handling & Restoration)

This test suite covers:
- Test Case 1: PERSON & AADHAAR detection, masking, encryption, and restoration.
- Test Case 2: EMAIL & PHONE detection, masking, encryption, and restoration.
- Test Case 3: Non-PII query ("What is Artificial Intelligence?") bypassing mapping.
- Test Case 4: LLM response containing no placeholders (response remains unchanged).
- Test Case 5: LLM response containing repeated placeholders (all restored correctly).
- Security checks: Encryption integrity, absence of plaintext PII in persistent files,
  and ordinary word protection during restoration.
"""

import os
import unittest
from unittest.mock import patch

from pii_detector import detect_pii
from masker import mask_pii, create_pii_mapping, mask_and_map_pii
from demasker import restore_pii
from storage.encrypted_store import (
    generate_key,
    encrypt_data,
    decrypt_data,
    save_encrypted,
    load_encrypted,
)
from pipeline import process_prompt


class TestPhase5SecurePIIHandling(unittest.TestCase):

    def setUp(self):
        self.test_storage_file = "storage/test_encrypted_mapping.bin"

    def tearDown(self):
        if os.path.exists(self.test_storage_file):
            try:
                os.remove(self.test_storage_file)
            except OSError:
                pass

    # =========================================================================
    # UNIT TESTS: DEMASKING & RESTORATION (Part 2)
    # =========================================================================

    def test_case_4_no_placeholders_in_response(self):
        """Test Case 4: LLM response contains no placeholders -> unchanged."""
        mapping = {
            "[PERSON]": "Ananya Iyer",
            "[AADHAAR]": "2222 3333 4444"
        }
        llm_response = "Artificial intelligence is a branch of computer science."
        restored = restore_pii(llm_response, mapping)

        self.assertEqual(restored, llm_response)

    def test_case_5_repeated_placeholders(self):
        """Test Case 5: LLM response contains repeated placeholders -> all restored."""
        mapping = {
            "[PERSON]": "Ananya Iyer"
        }
        llm_response = "Hello [PERSON]! We have recorded your account, [PERSON]. Welcome [PERSON]."
        expected = "Hello Ananya Iyer! We have recorded your account, Ananya Iyer. Welcome Ananya Iyer."

        restored = restore_pii(llm_response, mapping)
        self.assertEqual(restored, expected)

    def test_partial_placeholders(self):
        """Only some placeholders exist in LLM response."""
        mapping = {
            "[PERSON]": "Ananya Iyer",
            "[AADHAAR]": "2222 3333 4444",
            "[EMAIL]": "ananya@example.com"
        }
        llm_response = "Greetings [PERSON], an email has been sent to [EMAIL]."
        expected = "Greetings Ananya Iyer, an email has been sent to ananya@example.com."

        restored = restore_pii(llm_response, mapping)
        self.assertEqual(restored, expected)

    def test_ordinary_text_protection(self):
        """Ensure ordinary words (like 'person' or 'phone') are NOT replaced."""
        mapping = {
            "[PERSON]": "Ananya Iyer",
            "[PHONE]": "+91-90000-12345"
        }
        llm_response = "Every person should keep their phone secure. Hello [PERSON]."
        expected = "Every person should keep their phone secure. Hello Ananya Iyer."

        restored = restore_pii(llm_response, mapping)
        self.assertEqual(restored, expected)

    # =========================================================================
    # UNIT TESTS: MAPPING & ENCRYPTION (Part 1)
    # =========================================================================

    def test_mapping_structure_and_encryption(self):
        """Test clean mapping structure and AES-256-GCM encrypted persistence."""
        prompt = "My name is Ananya Iyer and my Aadhaar is 2222 3333 4444."
        detections = detect_pii(prompt)
        mapping = create_pii_mapping(detections)

        # Verify mapping keys and values
        self.assertIn("[PERSON]", mapping)
        self.assertIn("[AADHAAR]", mapping)
        self.assertEqual(mapping["[PERSON]"], "Ananya Iyer")
        self.assertEqual(mapping["[AADHAAR]"], "2222 3333 4444")

        # Encrypt and save
        key = generate_key()
        save_encrypted(mapping, key, filename=self.test_storage_file)

        # Verify persistent file is ciphertext (not plaintext JSON)
        with open(self.test_storage_file, "r") as f:
            raw_file_contents = f.read()

        self.assertNotIn("Ananya", raw_file_contents)
        self.assertNotIn("2222", raw_file_contents)
        self.assertNotIn("[PERSON]", raw_file_contents)

        # Decrypt and verify exact match
        decrypted = load_encrypted(key, filename=self.test_storage_file)
        self.assertEqual(decrypted, mapping)

    # =========================================================================
    # PIPELINE INTEGRATION TESTS (Part 3 & 4)
    # =========================================================================

    def test_case_1_ananya_aadhaar_pipeline(self):
        """
        Test Case 1:
        Input: 'My name is Ananya Iyer and my Aadhaar is 2222 3333 4444.'
        Expected: PERSON and AADHAAR detected, masked, encrypted, and restored.
        """
        prompt = "My name is Ananya Iyer and my Aadhaar is 2222 3333 4444."

        # Simulate LLM echoing the placeholders back
        simulated_llm_reply = "Hello [PERSON], your Aadhaar [AADHAAR] has been received."

        with patch("pipeline.ask_llm", return_value=simulated_llm_reply) as mock_llm:
            detections, masked_prompt, final_response = process_prompt(
                prompt,
                persist_mapping=True,
                storage_file=self.test_storage_file
            )

            # Check detections
            labels = [d["label"] for d in detections]
            self.assertIn("PERSON", labels)
            self.assertIn("AADHAAR", labels)

            # Verify masked prompt sent to LLM
            self.assertIn("[PERSON]", masked_prompt)
            self.assertIn("[AADHAAR]", masked_prompt)
            self.assertNotIn("Ananya Iyer", masked_prompt)
            self.assertNotIn("2222 3333 4444", masked_prompt)

            # Verify LLM only received the masked prompt
            mock_llm.assert_called_once_with(masked_prompt)

            # Verify final restored response
            expected_response = "Hello Ananya Iyer, your Aadhaar 2222 3333 4444 has been received."
            self.assertEqual(final_response, expected_response)

    def test_case_2_email_phone_pipeline(self):
        """
        Test Case 2:
        Input: 'My email is ananya@example.com and my phone is +91-90000-12345.'
        Expected: EMAIL and PHONE detected, masked, encrypted, and restored.
        """
        prompt = "My email is ananya@example.com and my phone is +91-90000-12345."

        simulated_llm_reply = "Contact confirmed for [EMAIL] and [PHONE]."

        with patch("pipeline.ask_llm", return_value=simulated_llm_reply) as mock_llm:
            detections, masked_prompt, final_response = process_prompt(
                prompt,
                persist_mapping=True,
                storage_file=self.test_storage_file
            )

            # Check detections
            labels = [d["label"] for d in detections]
            self.assertIn("EMAIL", labels)
            self.assertIn("PHONE", labels)

            # Verify masked prompt sent to LLM
            self.assertIn("[EMAIL]", masked_prompt)
            self.assertIn("[PHONE]", masked_prompt)
            self.assertNotIn("ananya@example.com", masked_prompt)
            self.assertNotIn("+91-90000-12345", masked_prompt)

            mock_llm.assert_called_once_with(masked_prompt)

            expected_response = "Contact confirmed for ananya@example.com and +91-90000-12345."
            self.assertEqual(final_response, expected_response)

    def test_case_3_non_pii_query(self):
        """
        Test Case 3:
        Input: 'What is Artificial Intelligence?'
        Expected: No PII, no mapping created, direct LLM response.
        """
        prompt = "What is Artificial Intelligence?"
        simulated_llm_reply = "Artificial Intelligence (AI) is the intelligence of machines."

        with patch("pipeline.ask_llm", return_value=simulated_llm_reply) as mock_llm:
            # Ensure no existing test file interferes
            if os.path.exists(self.test_storage_file):
                os.remove(self.test_storage_file)

            detections, masked_prompt, final_response = process_prompt(
                prompt,
                persist_mapping=True,
                storage_file=self.test_storage_file
            )

            self.assertEqual(detections, [])
            self.assertEqual(masked_prompt, prompt)
            self.assertEqual(final_response, simulated_llm_reply)

            # Verify LLM was sent original prompt
            mock_llm.assert_called_once_with(prompt)

            # Verify no mapping file was created for non-PII queries
            self.assertFalse(os.path.exists(self.test_storage_file))

    # =========================================================================
    # LIVE OLLAMA / LOCAL LLAMA 3 INTEGRATION TEST
    # =========================================================================

    def test_live_ollama_pipeline(self):
        """Live test against local Ollama Llama 3 to confirm end-to-end operation."""
        prompt = "My name is Ananya Iyer. Please say: Hello [PERSON]."
        detections, masked_prompt, final_response = process_prompt(prompt)

        self.assertTrue(len(detections) > 0)
        self.assertIn("[PERSON]", masked_prompt)
        self.assertNotIn("Ananya Iyer", masked_prompt)

        # Check that response was received from local Llama 3
        self.assertIsInstance(final_response, str)
        self.assertTrue(len(final_response) > 0)
        print("\n[Live Ollama Test Response]:", final_response.strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
