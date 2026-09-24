import spacy

nlp = spacy.load("en_core_web_sm")

text = """
My name is Priya Sharma and I live in Chennai.
My Aadhaar number is 2345 6789 0123.
My PAN is ABCDE1234F.
"""

doc = nlp(text)

for entity in doc.ents:
    print(entity.text, "→", entity.label_)