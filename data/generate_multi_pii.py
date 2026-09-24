import json
import random

names = [
    "Priya Sharma",
    "Rahul Kumar",
    "Ananya Iyer",
    "Arjun Menon",
    "Sneha Reddy"
]

phones = [
    "+91-90000-12345",
    "+91-90000-23456",
    "+91-90000-34567",
    "+91-90000-45678"
]

emails = [
    "priya@example.com",
    "rahul@example.com",
    "ananya@example.com",
    "arjun@example.com"
]

cities = [
    "Chennai",
    "Bengaluru",
    "Hyderabad",
    "Mumbai",
    "Pune"
]

templates = [
    ("My name is {name} and my phone number is {phone}.",
     ["name", "phone"]),

    ("I am {name} and you can email me at {email}.",
     ["name", "email"]),

    ("My name is {name} and I live in {city}.",
     ["name", "city"]),

    ("You can contact {name} at {phone}.",
     ["name", "phone"]),

    ("{name} lives in {city} and can be contacted at {phone}.",
     ["name", "city", "phone"]),

    ("Please send the report to {email}. My name is {name}.",
     ["email", "name"])
]


def create_multi_entity_example(template, fields):
    values = {
        "name": random.choice(names),
        "phone": random.choice(phones),
        "email": random.choice(emails),
        "city": random.choice(cities)
    }

    text = template.format(**values)

    label_map = {
        "name": "PERSON",
        "phone": "PHONE",
        "email": "EMAIL",
        "city": "LOCATION"
    }

    entities = []

    for field in fields:
        value = values[field]

        start = text.index(value)
        end = start + len(value)

        entities.append({
            "start": start,
            "end": end,
            "label": label_map[field]
        })

    return {
        "text": text,
        "entities": entities
    }


dataset = []

for template, fields in templates:
    for _ in range(200 // len(templates)):
        dataset.append(
            create_multi_entity_example(template, fields)
        )

random.shuffle(dataset)

with open("data/multi_pii_dataset.json", "w") as file:
    json.dump(dataset, file, indent=2)

print(f"Generated {len(dataset)} multi-PII examples.")