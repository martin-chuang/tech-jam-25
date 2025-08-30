# Anonymization function using PresidioEngine
def presidio_anonymize(text, engine):
    engine.analyze_text(text)
    anonymized_text = engine.anonymise_text(text)
    print(f"Original Text: {text}")
    print(f"Anonymized Text: {anonymized_text}")
    return anonymized_text
