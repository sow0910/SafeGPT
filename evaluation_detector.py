import json
from collections import defaultdict
from pii_detector import detect_pii


# Load test dataset
with open("data/test.json", "r") as f:
    test_data = json.load(f)


# Per-label counters
stats = defaultdict(lambda: {
    "TP": 0,
    "FP": 0,
    "FN": 0
})

# Overall counters
overall_tp = 0
overall_fp = 0
overall_fn = 0


for example in test_data:

    text = example["text"]
    actual_entities = example["entities"]

    # Predictions from our current detector
    predicted_entities = detect_pii(text)

    actual = set()

    for entity in actual_entities:
        actual.add(
            (
                entity["start"],
                entity["end"],
                entity["label"]
            )
        )

    predicted = set()

    for entity in predicted_entities:
        predicted.add(
            (
                entity["start"],
                entity["end"],
                entity["label"]
            )
        )

    # Correct predictions
    true_positives = actual & predicted

    # Predicted but not actually present
    false_positives = predicted - actual

    # Actual PII that detector missed
    false_negatives = actual - predicted


    # Overall counts
    overall_tp += len(true_positives)
    overall_fp += len(false_positives)
    overall_fn += len(false_negatives)


    # Per-label true positives
    for entity in true_positives:
        label = entity[2]
        stats[label]["TP"] += 1


    # Per-label false positives
    for entity in false_positives:
        label = entity[2]
        stats[label]["FP"] += 1


    # Per-label false negatives
    for entity in false_negatives:
        label = entity[2]
        stats[label]["FN"] += 1



# OVERALL METRICS

if overall_tp + overall_fp > 0:
    overall_precision = overall_tp / (overall_tp + overall_fp)
else:
    overall_precision = 0

if overall_tp + overall_fn > 0:
    overall_recall = overall_tp / (overall_tp + overall_fn)
else:
    overall_recall = 0

if overall_precision + overall_recall > 0:
    overall_f1 = (
        2
        * overall_precision
        * overall_recall
        / (overall_precision + overall_recall)
    )
else:
    overall_f1 = 0


print("\nOVERALL PII DETECTOR EVALUATION\n")

print("Test examples:", len(test_data))

print("\nTrue Positives :", overall_tp)
print("False Positives:", overall_fp)
print("False Negatives:", overall_fn)

print("\nPrecision:", round(overall_precision, 4))
print("Recall   :", round(overall_recall, 4))
print("F1-score :", round(overall_f1, 4))


# PER-LABEL METRICS

print("\n\n PER-LABEL PII EVALUATION \n")


for label in sorted(stats.keys()):

    tp = stats[label]["TP"]
    fp = stats[label]["FP"]
    fn = stats[label]["FN"]

    if tp + fp > 0:
        precision = tp / (tp + fp)
    else:
        precision = 0

    if tp + fn > 0:
        recall = tp / (tp + fn)
    else:
        recall = 0

    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0

    print(label)

    print(f"  TP: {tp}")
    print(f"  FP: {fp}")
    print(f"  FN: {fn}")

    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-score:  {f1:.4f}")

    print()