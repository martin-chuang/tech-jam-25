from app.components.rag.rag_engine import State

def text_to_document(text, engine):
    return engine.text_to_document(text)

def add_to_vector_db(document, engine):
    engine.store_documents([document])

def retrieve_context(query, engine):
    state: State = {"question": query}
    return engine.retrieve_context(state)

def invoke_conversation(query, engine):
    state: State = {"question": query}
    return engine.invoke_conversation(state)