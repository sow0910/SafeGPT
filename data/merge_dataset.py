import json

with open("data/pii_dataset_generated.json", "r") as file:
    single_pii = json.load(file)

with open("data/multi_pii_dataset.json", "r") as file:
    multi_pii = json.load(file)

final_dataset = single_pii + multi_pii

with open("data/final_pii_dataset.json", "w") as file:
    json.dump(final_dataset, file, indent=2)

print(f"Final dataset size: {len(final_dataset)}")