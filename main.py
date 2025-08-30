from flask import Flask, request, jsonify
from app.components.embedding_model.embedding_model import EmbeddingModel
from app.components.presidio.presidio_engine import PresidioEngine
from app.components.rag.rag_engine import RAGEngine
from app.components.homomorphic_encryption.encryption_engine import HEManager
# from app.components.redis.redis_engine import RedisEngine
from app.components.llm.llm_engine import LLMEngine

# Initialise cloud LLM Gemini
from dotenv import load_dotenv
import os
# Load environment variables from .env file and set api key to environment variable
load_dotenv()
from langchain.chat_models import init_chat_model
os.environ['GOOGLE_API_KEY'] = os.getenv("GOOGLE_API_KEY")

# Dependency Injection
cloud_llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
embedding_model = EmbeddingModel(backend="mini-lm")
presidio_engine = PresidioEngine(embedding_model)
rag_engine = RAGEngine(embedding_model, cloud_llm)
# redis_engine = RedisEngine()
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

@app.route('/query-model', methods=['POST'])
def query_model():
    data = request.json
    context = data.get("context", "")
    query = data.get("query", "")
    message_chain = query_model_final(query, context)
    return message_chain, 200

def query_model_final(query, context):
    # Preprocess context
    rag_engine.analyze_text(context)
    anonymized_context = rag_engine.anonymise_text(context)
    encrypted_context = encryption_engine.encrypt(anonymized_context)
    # Convert anonymized context to embeddings
    documents = rag_engine.text_to_document(anonymized_context)
    embedding_obj_list = rag_engine.generate_key_and_embeddings(documents)
    for embedding_obj in embedding_obj_list:
        # Store anonymized context in vector DB
        rag_engine.store_embeddings(embedding_obj['embedding'], embedding_obj['id'])
        # Store encrypter context in redis
        # redis_engine.set(embedding_obj['id'], embedding_obj['context'])

    # Preprocess query
    rag_engine.analyze_text(query)
    anonymized_query = rag_engine.anonymise_text(query)

    # Retrieve encrypted context_ids
    retrieved_context_ids = rag_engine.retrieve_context_ids(anonymized_query)

    # Retrieve encrypted context using context_ids and decrypt them
    print(f"Retrieved context ids: {retrieved_context_ids}")
    decrypted_context_str = ""
    for id in retrieved_context_ids:
        # encrypted_context = redis_engine.get(id)
        decrypted_context = encryption_engine.decrypt(encrypted_context)
        deanonymized_context = rag_engine.de_anonymise_text(decrypted_context)
        decrypted_context_str += f"{deanonymized_context}\n"

    # Query model with decrypted context (both uses anonymized data)
    message_chain = llm_engine.query_model(anonymized_query, decrypted_context_str)
    return message_chain

if(__name__) == '__main__':
    print("Running app")
    app.run(host="0.0.0.0", port = 5050, debug=True)