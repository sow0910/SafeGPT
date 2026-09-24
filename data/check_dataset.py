import json
from collections import Counter

with open("data/final_pii_dataset.json", "r") as file:
    dataset = json.load(file)

label_counts = Counter()

for example in dataset:
    for entity in example["entities"]:
        label_counts[entity["label"]] += 1

print("Total examples:", len(dataset))
print("\nEntity distribution:")

for label, count in sorted(label_counts.items()):
    print(f"{label}: {count}")