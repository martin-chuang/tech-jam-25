from flask import Flask, request, jsonify
from app.components.embedding_model.embedding_model import EmbeddingModel
from app.components.presidio.presidio_engine import PresidioEngine
from app.components.rag.rag_engine import RAGEngine
from app.service.presidio_service import presidio_anonymize
from app.service.rag_service import *

# Initialize cloud LLM (currently using local Ollama model)
from langchain_ollama import ChatOllama
cloud_llm = ChatOllama(model="phi3:latest")

# Dependency Injection
embedding_model = EmbeddingModel(backend="mini-lm")
presidio_engine = PresidioEngine(embedding_model)
rag_engine = RAGEngine(embedding_model, cloud_llm)
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
    anonymized_text = presidio_anonymize(text, presidio_engine) # Execute service layer
    response = {
        "status": "success",
        "body": anonymized_text
    }
    return jsonify(response), 200

@app.route('/consume-context', methods=['POST'])
def consume_context():
    data = request.json
    text = data.get("body", "")
    # text = "His name is Mr. Jones, Jones Bond and his phone number is 212-555-5555. Jones is friends with Martin."
    doc = text_to_document(text, rag_engine)
    add_to_vector_db(doc, rag_engine)
    response = {
        "status": "success",
        "body": "Context added to vector database"
    }
    return jsonify(response), 200

@app.route('/query-model', methods=['POST'])
def query_model():
    data = request.json
    query = data.get("body", "")
    # query = "What is Jones' phone number?"
    state = invoke_conversation(query, rag_engine)
    print(f"""
          Question: {query}\n
          Answer: {state['answer']}\n
          Context: {state['context']}
""")
    response = {
        "status": "success",
        "body": state['answer']
    }
    return jsonify(response), 200

if(__name__) == '__main__':
    app.run(debug=True)