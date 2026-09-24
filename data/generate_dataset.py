import json
import random

# -----------------------------
# Synthetic Indian PII values
# -----------------------------

names = [
    "Priya Sharma",
    "Rahul Kumar",
    "Ananya Iyer",
    "Arjun Menon",
    "Sneha Reddy",
    "Vikram Patel",
    "Kavya Nair",
    "Rohan Gupta",
    "Meera Krishnan",
    "Aditya Rao"
]

cities = [
    "Chennai",
    "Bengaluru",
    "Hyderabad",
    "Mumbai",
    "Delhi",
    "Pune",
    "Kochi",
    "Coimbatore",
    "Madurai",
    "Mysuru"
]

phone_numbers = [
    "+91-90000-12345",
    "+91-90000-23456",
    "+91-90000-34567",
    "+91-90000-45678",
    "+91-90000-56789"
]

emails = [
    "priya@example.com",
    "rahul@example.com",
    "ananya@example.com",
    "arjun@example.com",
    "sneha@example.com"
]

pincodes = [
    "600042",
    "560001",
    "500001",
    "400001",
    "110001",
    "411001",
    "682001",
    "641001",
    "625001",
    "570001"
]
pans = [
    "ABCDE1234F",
    "FGHIJ5678K",
    "LMNOP9012Q",
    "RSTUV3456W",
    "XYZAB7890C"
]

aadhaars = [
    "1111 2222 3333",
    "2222 3333 4444",
    "3333 4444 5555",
    "4444 5555 6666",
    "5555 6666 7777"
]

addresses = [
    "12 Anna Nagar, Chennai",
    "45 MG Road, Bengaluru",
    "78 Banjara Hills, Hyderabad",
    "23 Koregaon Park, Pune",
    "56 Marine Drive, Mumbai"
]

dobs = [
    "15/08/1999",
    "21/03/2000",
    "10/12/1998",
    "05/06/2001",
    "28/11/1997"
]

passports = [
    "P1234567",
    "P2345678",
    "P3456789",
    "P4567890",
    "P5678901"
]
# -----------------------------
# Templates
# -----------------------------

person_templates = [
    "My name is {value}.",
    "I am {value}.",
    "Please register my name as {value}.",
    "The patient's name is {value}.",
    "You can call me {value}."
]

phone_templates = [
    "My phone number is {value}.",
    "You can contact me at {value}.",
    "Please call me on {value}.",
    "My registered number is {value}.",
    "You can reach me at {value}."
]

email_templates = [
    "My email address is {value}.",
    "Please send the report to {value}.",
    "You can email me at {value}.",
    "My registered email is {value}.",
    "Contact me through {value}."
]

location_templates = [
    "I currently live in {value}.",
    "I am staying in {value}.",
    "The patient is from {value}.",
    "My current location is {value}.",
    "I live near {value}."
]

pincode_templates = [
    "My PIN code is {value}.",
    "The postal code is {value}.",
    "Please use PIN {value}.",
    "My area PIN is {value}.",
    "The delivery PIN code is {value}."
]

pan_templates = [
    "My PAN is {value}.",
    "Please provide my PAN as {value}.",
    "The registered PAN is {value}.",
    "My PAN number is {value}.",
    "Please update the PAN to {value}."
]

aadhaar_templates = [
    "My Aadhaar number is {value}.",
    "The Aadhaar number is {value}.",
    "Please verify Aadhaar {value}.",
    "My Aadhaar is {value}.",
    "The registered Aadhaar number is {value}."
]

address_templates = [
    "My address is {value}.",
    "I currently live at {value}.",
    "Please deliver it to {value}.",
    "The patient's address is {value}.",
    "My registered address is {value}."
]

dob_templates = [
    "My date of birth is {value}.",
    "I was born on {value}.",
    "The patient's DOB is {value}.",
    "My birth date is {value}.",
    "Please record my DOB as {value}."
]

passport_templates = [
    "My passport number is {value}.",
    "The passport number is {value}.",
    "Please record passport {value}.",
    "My registered passport is {value}.",
    "The patient's passport number is {value}."
]


# -----------------------------
# Entity creation
# -----------------------------

def create_example(text, value, label):
    start = text.index(value)
    end = start + len(value)

    return {
        "text": text,
        "entities": [
            {
                "start": start,
                "end": end,
                "label": label
            }
        ]
    }


# -----------------------------
# Generate dataset
# -----------------------------

dataset = []

for _ in range(100):
    value = random.choice(names)
    template = random.choice(person_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "PERSON"))

for _ in range(100):
    value = random.choice(phone_numbers)
    template = random.choice(phone_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "PHONE"))

for _ in range(100):
    value = random.choice(emails)
    template = random.choice(email_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "EMAIL"))

for _ in range(100):
    value = random.choice(cities)
    template = random.choice(location_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "LOCATION"))

for _ in range(100):
    value = random.choice(pincodes)
    template = random.choice(pincode_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "PINCODE"))

for _ in range(100):
    value = random.choice(pans)
    template = random.choice(pan_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "PAN"))

for _ in range(100):
    value = random.choice(aadhaars)
    template = random.choice(aadhaar_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "AADHAAR"))

for _ in range(100):
    value = random.choice(addresses)
    template = random.choice(address_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "ADDRESS"))

for _ in range(100):
    value = random.choice(dobs)
    template = random.choice(dob_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "DOB"))

for _ in range(100):
    value = random.choice(passports)
    template = random.choice(passport_templates)
    text = template.format(value=value)
    dataset.append(create_example(text, value, "PASSPORT"))
# -----------------------------
# Save dataset
# -----------------------------

random.shuffle(dataset)

with open("data/pii_dataset_generated.json", "w") as file:
    json.dump(dataset, file, indent=2)

print(f"Generated {len(dataset)} examples.")