from flask import Flask, request, jsonify
from app.service.presidio_service import presidio_anonymize
from app.components.presidio.presidio_engine import PresidioEngine

# Dependency Injection - Initialize PresidioEngine once
engine = PresidioEngine(model="mini-lm")
app = Flask(__name__)

# API endpoints
@app.route('/')
def hello_world():
    response = {
        "status": "success",
        "body": 'Hello this is flask'
    }
    return jsonify(response), 200

@app.route('/anonymize', methods=['POST'])
def anonymize_text():
    data = request.json
    text = data.get("body", "")
    anonymized_text = presidio_anonymize(text, engine) # Execute service layer
    response = {
        "status": "success",
        "body": anonymized_text
    }
    return jsonify(response), 200

#Example API call
# text_input = {"body": "His name is Mr. Jones, Jones Bond and his phone number is 212-555-5555. Jones is friends with Martin"}

if(__name__) == '__main__':
    app.run(debug=True)