"""
Run measured FL privacy–utility experiments and the 10-category PII demo.

Outputs:
  data/fl_experiment_results.json
  data/pii_demo_10cat.json
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from pii_detector import detect_pii
from masker import mask_pii, create_pii_mapping
from demasker import restore_pii
from storage.encrypted_store import generate_key, encrypt_data, decrypt_data
from federated.simulation import compare_dp_tradeoffs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

TEN_CAT_PROMPT = (
    "My name is Ananya Iyer. My Aadhaar is 2222 3333 4444. My PAN is ABCDE1234F. "
    "My passport is A1234567. I was born on 15/08/2003. I currently live in Chennai. "
    "My registered address is 45 MG Road, Bengaluru with PIN 560001. "
    "Please reach me at ananya@example.com or call +91-90000-12345. "
    "Can you summarize all my details?"
)

EXPECTED_LABELS = [
    "PERSON",
    "AADHAAR",
    "PAN",
    "PHONE",
    "EMAIL",
    "ADDRESS",
    "LOCATION",
    "DOB",
    "PASSPORT",
    "PINCODE",
]


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def run_fl_experiments(rounds: int = 5) -> Dict[str, Any]:
    raw = compare_dp_tradeoffs(rounds=rounds)
    table_rows: List[Dict[str, Any]] = []
    for item in raw:
        hist = item["history"]
        round_map = {h["round"]: h["val_accuracy"] for h in hist}
        row = {
            "experiment": item["scenario"],
            "dp_enabled": bool(item["use_dp"]),
            "epsilon": item["epsilon"],
            "privacy": item["privacy"],
            "communication_rounds": rounds,
            "initial_accuracy": item["initial_accuracy"],
            "initial_accuracy_pct": _pct(item["initial_accuracy"]),
            "final_accuracy": item["final_accuracy"],
            "final_accuracy_pct": _pct(item["final_accuracy"]),
            "final_loss": item["final_loss"],
            "round_1_pct": _pct(round_map.get(1, 0.0)),
            "round_2_pct": _pct(round_map.get(2, 0.0)),
            "round_3_pct": _pct(round_map.get(3, 0.0)),
            "round_4_pct": _pct(round_map.get(4, 0.0)),
            "round_5_pct": _pct(round_map.get(5, 0.0)),
            "history": hist,
        }
        table_rows.append(row)

    payload = {
        "note": "Results are from a simulated three-client environment (Hospital A/B/C), not a live hospital network.",
        "clients": [
            {"client_id": "Hospital_A", "num_samples": 300},
            {"client_id": "Hospital_B", "num_samples": 200},
            {"client_id": "Hospital_C", "num_samples": 150},
        ],
        "clipping_norm": 1.0,
        "delta": 1e-5,
        "rounds": rounds,
        "experiments": table_rows,
    }
    out_path = os.path.join(DATA_DIR, "fl_experiment_results.json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return payload


def run_ten_category_demo() -> Dict[str, Any]:
    detections = detect_pii(TEN_CAT_PROMPT)
    labels = [d["label"] for d in detections]
    unique_labels = sorted(set(labels))
    masked = mask_pii(TEN_CAT_PROMPT, detections)
    mapping = create_pii_mapping(detections)
    key = generate_key()
    ciphertext = encrypt_data(mapping, key)
    decrypted = decrypt_data(ciphertext, key)

    simulated_llm = (
        "Summary for [PERSON]: identifiers recorded as [AADHAAR], [PAN], [PASSPORT]; "
        "date of birth [DOB]; city [LOCATION]; address [ADDRESS]; PIN [PINCODE]; "
        "email [EMAIL]; phone [PHONE]."
    )
    restored = restore_pii(simulated_llm, decrypted)

    original_values = [d["text"] for d in detections]
    leaked_in_masked = [value for value in original_values if value in masked]
    restored_ok = all(decrypted[token] in restored for token in decrypted)

    payload = {
        "prompt": TEN_CAT_PROMPT,
        "detected_count": len(detections),
        "detected_labels": labels,
        "unique_labels": unique_labels,
        "expected_labels": EXPECTED_LABELS,
        "missing_expected_labels": [lab for lab in EXPECTED_LABELS if lab not in unique_labels],
        "masked_prompt": masked,
        "ciphertext_chars": len(ciphertext),
        "ciphertext_preview": ciphertext[:80] + "...",
        "mapping_keys": sorted(decrypted.keys()),
        "simulated_llm_output": simulated_llm,
        "restored_response": restored,
        "pii_values_remaining_in_masked_prompt": leaked_in_masked,
        "restoration_succeeded": restored_ok,
        "round_trip_mapping_match": decrypted == mapping,
        "llm_note": "Llama inference is demonstrated in the live dashboard; this recorded demo uses a placeholder-preserving simulated LLM output so the restoration path can be measured without depending on Ollama availability.",
    }
    out_path = os.path.join(DATA_DIR, "pii_demo_10cat.json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return payload


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    fl = run_fl_experiments()
    demo = run_ten_category_demo()
    print("Wrote data/fl_experiment_results.json")
    for row in fl["experiments"]:
        eps = "None" if row["epsilon"] is None else row["epsilon"]
        print(
            f"  {row['experiment']}: init={row['initial_accuracy_pct']} "
            f"R1={row['round_1_pct']} R2={row['round_2_pct']} R3={row['round_3_pct']} "
            f"R4={row['round_4_pct']} R5={row['round_5_pct']} loss={row['final_loss']:.4f} ε={eps}"
        )
    print("Wrote data/pii_demo_10cat.json")
    print("  detected_count:", demo["detected_count"])
    print("  unique_labels:", ", ".join(demo["unique_labels"]))
    print("  missing_expected_labels:", demo["missing_expected_labels"])
    print("  leaked_in_masked:", demo["pii_values_remaining_in_masked_prompt"])
    print("  restoration_succeeded:", demo["restoration_succeeded"])
