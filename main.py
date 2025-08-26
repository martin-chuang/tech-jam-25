from app.service.presidio_service import presidio_anonymize
from app.components.presidio.presidio_engine import PresidioEngine

# Dependency Injection - Initialize PresidioEngine once
engine = PresidioEngine(model="mini-lm")

# API
def anonymize_text(text):
    anonymized_text = presidio_anonymize(text, engine) # Execute service layer
    return anonymized_text

#Example API call
text_input = "His name is Mr. Jones, Jones Bond and his phone number is 212-555-5555. Jones is friends with Martin"
print(anonymize_text(text_input))