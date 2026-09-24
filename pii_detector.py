import re
import spacy

nlp = spacy.load("en_core_web_sm")
def detect_aadhaar(text):
    """
    Detect an Aadhaar-like 12-digit number.
    """

    pattern = r"\b\d{4}\s\d{4}\s\d{4}\b"

    matches = re.finditer(pattern, text)

    results = []

    for match in matches:
        results.append({
            "text": match.group(),
            "label": "AADHAAR",
            "start": match.start(),
            "end": match.end()
        })

    return results

def detect_pan(text):
    """
    Detect a PAN-like 10-character identifier.
    """

    pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

    matches = re.finditer(pattern, text)

    results = []

    for match in matches:
        results.append({
            "text": match.group(),
            "label": "PAN",
            "start": match.start(),
            "end": match.end()
        })

    return results

def detect_phone(text):
    """
    Detect common Indian phone number formats.
    """

    pattern = r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?!\d)"

    matches = re.finditer(pattern, text)

    results = []

    for match in matches:
        results.append({
            "text": match.group(),
            "label": "PHONE",
            "start": match.start(),
            "end": match.end()
        })

    return results
def detect_email(text):
    """
    Detect email addresses.
    """

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    matches = re.finditer(pattern, text)

    results = []

    for match in matches:
        results.append({
            "text": match.group(),
            "label": "EMAIL",
            "start": match.start(),
            "end": match.end()
        })

    return results
def detect_pincode(text):
    """
    Detect Indian 6-digit PIN codes.
    """

    pattern = r"(?<!\d)[1-9]\d{5}(?!\d)"

    matches = re.finditer(pattern, text)

    results = []

    for match in matches:
        results.append({
            "text": match.group(),
            "label": "PINCODE",
            "start": match.start(),
            "end": match.end()
        })

    return results


def detect_dob(text):
    """
    Detect common date-of-birth formats.
    """

    pattern = r"\b(?:0?[1-9]|[12]\d|3[01])[-/](?:0?[1-9]|1[0-2])[-/](?:19|20)\d{2}\b"

    matches = re.finditer(pattern, text)

    results = []

    for match in matches:
        results.append({
            "text": match.group(),
            "label": "DOB",
            "start": match.start(),
            "end": match.end()
        })

    return results


def detect_passport(text):
    """
    Detect an Indian passport-like identifier.
    """

    pattern = r"\b[A-Z][0-9]{7}\b"

    matches = re.finditer(pattern, text)

    results = []

    for match in matches:
        results.append({
            "text": match.group(),
            "label": "PASSPORT",
            "start": match.start(),
            "end": match.end()
        })

    return results


def detect_address(text):
    """
    Detect common Indian address formats.

    Examples:
    24, Anna Road
    45 MG Road, Bengaluru
    12 Anna Nagar, Chennai
    56 Marine Drive, Mumbai
    78 Banjara Hills, Hyderabad
    23 Koregaon Park, Pune
    """

    patterns = [

        # Format 1:
        # 24, Anna Road
        r"\b\d{1,5},\s*[A-Za-z0-9 .'-]+(?:Road|Rd|Street|St|Nagar|Colony|Layout|Avenue|Ave)\b",

        # Format 2:
        # 45 MG Road, Bengaluru
        # 12 Anna Nagar, Chennai
        # 56 Marine Drive, Mumbai
        # 78 Banjara Hills, Hyderabad
        # 23 Koregaon Park, Pune
        r"\b\d{1,5}\s+[A-Za-z0-9 .'-]+,\s*[A-Za-z .'-]+\b"
    ]

    results = []

    for pattern in patterns:

        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:

            results.append({
                "text": match.group(),
                "label": "ADDRESS",
                "start": match.start(),
                "end": match.end()
            })

    return results
def detect_location_rule(text):
    """
    Detect Indian city names using contextual phrases.
    This acts as a fallback when spaCy NER misses a location.
    """

    cities = [
        "Pune",
        "Hyderabad",
        "Chennai",
        "Mumbai",
        "Bengaluru",
        "Delhi",
        "Kolkata",
        "Ahmedabad"
    ]

    context_pattern = (
        r"\b(?:live in|lives in|from|located in|residing in)\s+"
        r"(" + "|".join(cities) + r")\b"
    )

    matches = re.finditer(
        context_pattern,
        text,
        re.IGNORECASE
    )

    results = []

    for match in matches:

        city = match.group(1)

        start = match.start(1)
        end = match.end(1)

        results.append({
            "text": city,
            "label": "LOCATION",
            "start": start,
            "end": end
        })

    return results

def detect_person_rule(text):

    patterns = [

        # My name is Ananya Iyer
        r"\b[Mm][Yy]\s+[Nn][Aa][Mm][Ee]\s+[Ii][Ss]\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",

        # The patient's name is Ananya Iyer
        r"\b[Tt]he\s+[Pp]atient's\s+[Nn]ame\s+[Ii]s\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",

        # Register my name as Kavya Nair
        r"\b[Rr]egister\s+[Mm]y\s+[Nn]ame\s+[Aa]s\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",

        # Ananya Iyer lives in Mumbai
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+lives in\b",

        # Ananya Iyer can be contacted
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+can be contacted\b"
    ]

    results = []

    for pattern in patterns:

        matches = re.finditer(pattern, text)

        for match in matches:

            name = match.group(1)

            results.append({
                "text": name,
                "label": "PERSON",
                "start": match.start(1),
                "end": match.end(1)
            })

    return results
def detect_ner(text):
    """
    Detect general named entities using spaCy.
    """

    doc = nlp(text)

    results = []

    for ent in doc.ents:

        if ent.label_ in ["PERSON", "GPE"]:

            # Filter obvious false-positive general concepts misidentified by spaCy
            if ent.text.strip().lower() in {"artificial intelligence", "machine learning", "deep learning"}:
                continue

            label = "PERSON" if ent.label_ == "PERSON" else "LOCATION"

            results.append({
                "text": ent.text,
                "label": label,
                "start": ent.start_char,
                "end": ent.end_char
            })

    return results

def detect_pii(text):
    """
    Detect PII using both custom rules and spaCy NER.
    Custom rule detections have priority over spaCy detections.
    """

    # Step 1: Detect specific Indian PII using our rules in priority order
    raw_rules = []
    raw_rules.extend(detect_aadhaar(text))
    raw_rules.extend(detect_pan(text))
    raw_rules.extend(detect_phone(text))
    raw_rules.extend(detect_email(text))
    raw_rules.extend(detect_pincode(text))
    raw_rules.extend(detect_dob(text))
    raw_rules.extend(detect_passport(text))
    raw_rules.extend(detect_person_rule(text))
    raw_rules.extend(detect_location_rule(text))
    raw_rules.extend(detect_address(text))

    # Keep rule detections only if they do not overlap with higher-priority rules
    rule_results = []
    for r in raw_rules:
        r_start = r["start"]
        r_end = r["end"]
        overlaps = False
        for kept in rule_results:
            if r_start < kept["end"] and r_end > kept["start"]:
                overlaps = True
                break
        if not overlaps:
            rule_results.append(r)

    # Step 2: Detect general entities using spaCy
    ner_results = detect_ner(text)

    # Step 3: Keep spaCy detections only if they do not
    # overlap with an existing rule-based detection
    final_results = rule_results.copy()

    for ner in ner_results:

        ner_start = ner["start"]
        ner_end = ner["end"]

        overlaps = False

        for rule in rule_results:

            rule_start = rule["start"]
            rule_end = rule["end"]

            # Check whether the two spans overlap
            if ner_start < rule_end and ner_end > rule_start:
                overlaps = True
                break

        if not overlaps:
            final_results.append(ner)

    # Step 4: Sort everything by position in the original text
    final_results.sort(key=lambda x: x["start"])

    return final_results

if __name__ == "__main__":

    text = """
    My name is Priya Sharma.
    I live in Chennai.
    My company is Infosys.
    My birthday is 15/08/2002.
    My Aadhaar number is 2345 6789 0123.
    My PAN is ABCDE1234F.
    My address is 24, Anna Road.
    """

    all_results = detect_pii(text)

    print("Final Detected PII:\n")

    for result in all_results:
        print(result)

if __name__ == "__main__":

    test_text = """
    I currently live in Pune.
    The patient is from Chennai.
    Arjun Menon lives in Hyderabad.
    Sneha Reddy lives in Mumbai.
    """

    results = detect_location_rule(test_text)

    print("\n===== LOCATION RULE TEST =====\n")

    for result in results:
        print(result)

    test_person_text = """
    My name is Ananya Iyer.
    Please register my name as Kavya Nair.
    The patient's name is Ananya Iyer.
    """

    print("\n===== PERSON RULE TEST =====\n")

    for result in detect_person_rule(test_person_text):
        print(result)

    print("\n===== DIRECT PERSON RULE CHECK =====\n")

    test = "My name is Ananya Iyer and I live in Chennai."

    print("PERSON RULE:")
    print(detect_person_rule(test))

    print("\nDETECT PII:")
    print(detect_pii(test))
