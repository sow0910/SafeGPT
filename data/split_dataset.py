import json
import random

# Load final dataset
with open("data/final_pii_dataset.json", "r") as file:
    dataset = json.load(file)

# Shuffle reproducibly
random.seed(42)
random.shuffle(dataset)

# 80% training, 20% testing
split_index = int(len(dataset) * 0.8)

train_data = dataset[:split_index]
test_data = dataset[split_index:]

# Save training data
with open("data/train.json", "w") as file:
    json.dump(train_data, file, indent=2)

# Save testing data
with open("data/test.json", "w") as file:
    json.dump(test_data, file, indent=2)

print("Total examples:", len(dataset))
print("Training examples:", len(train_data))
print("Testing examples:", len(test_data))