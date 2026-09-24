import json
from pii_detector import detect_pii


# Load test dataset
with open("data/test.json", "r") as f:
    test_data = json.load(f)


def analyze_address_errors():

    print("\n===== MISSED ADDRESS ERRORS =====\n")

    for example in test_data:

        text = example["text"]
        actual_entities = example["entities"]

        predicted_entities = detect_pii(text)

        predicted = {
            (
                entity["start"],
                entity["end"],
                entity["label"]
            )
            for entity in predicted_entities
        }

        for entity in actual_entities:

            if entity["label"] != "ADDRESS":
                continue

            actual = (
                entity["start"],
                entity["end"],
                entity["label"]
            )

            if actual not in predicted:

                print("TEXT:")
                print(text)

                print("\nACTUAL ADDRESS:")
                print(entity)

                print("\nWHAT DETECTOR FOUND:")
                print(predicted_entities)

                print("\n" + "-" * 70)


def analyze_location_errors():

    print("\n===== MISSED LOCATION ERRORS =====\n")

    for example in test_data:

        text = example["text"]
        actual_entities = example["entities"]

        predicted_entities = detect_pii(text)

        predicted = {
            (
                entity["start"],
                entity["end"],
                entity["label"]
            )
            for entity in predicted_entities
        }

        for entity in actual_entities:

            if entity["label"] != "LOCATION":
                continue

            actual = (
                entity["start"],
                entity["end"],
                entity["label"]
            )

            if actual not in predicted:

                print("TEXT:")
                print(text)

                print("\nACTUAL LOCATION:")
                print(entity)

                print("\nWHAT DETECTOR FOUND:")
                print(predicted_entities)

                print("\n" + "-" * 70)

def analyze_person_errors():

    print("\n===== PERSON ERRORS =====\n")

    for example in test_data:

        text = example["text"]
        actual_entities = example["entities"]

        # Run our detector
        predicted_entities = detect_pii(text)

        # -----------------------------
        # Check MISSED PERSON (FN)
        # -----------------------------

        predicted = {
            (
                entity["start"],
                entity["end"],
                entity["label"]
            )
            for entity in predicted_entities
        }

        for entity in actual_entities:

            if entity["label"] != "PERSON":
                continue

            actual = (
                entity["start"],
                entity["end"],
                entity["label"]
            )

            if actual not in predicted:

                print("MISSED PERSON (FN):")

                print("TEXT:")
                print(text)

                print("\nACTUAL PERSON:")
                print(entity)

                print("\nWHAT DETECTOR FOUND:")
                print(predicted_entities)

                print("\n" + "-" * 70)


        # -----------------------------
        # Check INCORRECT PERSON (FP)
        # -----------------------------

        actual_persons = {
            (
                entity["start"],
                entity["end"],
                entity["label"]
            )
            for entity in actual_entities
            if entity["label"] == "PERSON"
        }

        for prediction in predicted_entities:

            if prediction["label"] != "PERSON":
                continue

            predicted_person = (
                prediction["start"],
                prediction["end"],
                prediction["label"]
            )

            if predicted_person not in actual_persons:

                print("INCORRECT PERSON (FP):")

                print("TEXT:")
                print(text)

                print("\nINCORRECT PREDICTION:")
                print(prediction)

                print("\nACTUAL ENTITIES:")
                print(actual_entities)

                print("\n" + "-" * 70)

# Run ADDRESS analysis
analyze_address_errors()

# Run LOCATION analysis
analyze_location_errors()


analyze_person_errors()

print("\n===== DEBUG PERSON =====\n")

text = "My name is Ananya Iyer and I live in Chennai."

print("TEXT:")
print(text)

print("\nDETECTOR OUTPUT:")

for result in detect_pii(text):
    print(result)