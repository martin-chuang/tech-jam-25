from flask import Flask, request, jsonify
from app.components.embedding_model.embedding_model import EmbeddingModel
from app.components.presidio.presidio_engine import PresidioEngine
from app.components.rag.rag_engine import RAGEngine
from app.components.llm.llm_engine import LLMEngine
from app.components.homomorphic_encryption.encryption_engine import HEManager
from app.service.presidio_service import presidio_anonymize
from app.service.rag_service import *
from app.service.anonymize_encryptor_service import anonymize_and_encrypt

# Initialize cloud LLM (currently using local Ollama model)
# from langchain_ollama import ChatOllama
# cloud_llm = ChatOllama(model="phi3:latest")

# Initialise cloud LLM Gemini
from dotenv import load_dotenv
import os
# Load environment variables from .env file and set api key to environment variable
load_dotenv()

from langchain.chat_models import init_chat_model
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")
cloud_llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
cloud_llm.invoke("Sing a ballad of LangChain.")

# Dependency Injection
embedding_model = EmbeddingModel(backend="mini-lm")
presidio_engine = PresidioEngine(embedding_model)
rag_engine = RAGEngine(embedding_model, cloud_llm)
llm_engine = LLMEngine(cloud_llm)
encryption_engine = HEManager()
app = Flask(__name__)

# API endpoints
@app.route('/')
def hello_world():
    response = {
        "status": "success",
        "body": 'Hello this is flask'
    }
    return jsonify(response), 200

@app.route('/test-llm', methods=['POST'])
def test_llm():
    data = request.json
    prompt = data.get("body", "")
    # response = cloud_llm.invoke(prompt)
    response = cloud_llm.invoke("Hello world, this is a test. Just reply with 'Hello from Gemini'.")
    print(response)
    result = {
        "status": "success",
        "body": response.content
    }
    return jsonify(result), 200

@app.route('/anonymize_encrypt', methods=['POST'])
def anonymize_and_encrypt_text():
    data = request.json
    text = data.get("body", "")
    anonymized_text = presidio_anonymize(text, presidio_engine) # Execute service layer
    encrypted_text = encryption_engine.encrypt(anonymized_text)
    response = {
        "status": "success",
        "body": encrypted_text
    }
    return jsonify(response), 200

@app.route('/consume-context', methods=['POST'])
def consume_context():
    data = request.json
    text = data.get("body", "")
    # text = "His name is Mr. Jones, Jones Bond and his phone number is 212-555-5555."
    # text = "Jones is friends with Martin."
    # text = "Jones likes to play football on 5th avenue."

    processed_text = anonymize_and_encrypt(text)
    doc = text_to_document(processed_text, rag_engine)
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

    # Retrieve context
    state: State = {"question": query}
    context = rag_engine.retrieve_context(state)
    # context = retrieve_context(query, rag_engine)
    decrypted_context = encryption_engine.decrypt(context)
    message_chain = rag_engine.query_model(query, decrypted_context)
    return message_chain, 200

@app.route('/query-model-final', methods=['POST'])
def query_model_final(query, context):
    # Preprocess context
    rag_engine.analyze_text(context)
    anonymized_context = rag_engine.anonymise_text(context)
    encrypted_context = encryption_engine.encrypt(anonymized_context)
        # Store encrypted context in vector DB
    doc = rag_engine.text_to_document(encrypted_context)
    rag_engine.store_documents([doc])

    # Preprocess query
    rag_engine.analyze_text(query)
    anonymized_query = rag_engine.anonymise_text(query)
    encrypted_query = encryption_engine.encrypt(anonymized_query)

    # Retrieve encrypted context
    state: State = {"question": encrypted_query}
    context = rag_engine.retrieve_context(state)

    # Decrypt context (anonymized)
    decrypted_context = encryption_engine.decrypt(context)

    # Query model with decrypted context (both uses anonymized data)
    message_chain = llm_engine.query_model(anonymized_query, decrypted_context)
    print("\n Main.py message_chain:", message_chain)
    return message_chain

if(__name__) == '__main__':
    app.run(debug=True)