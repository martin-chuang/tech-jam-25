from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langgraph.graph import START, StateGraph
from langchain import hub

# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

class RAGEngine:
    def __init__(self, embedding_model, llm):
        # self.embedding_model = embedding_model
        self.llm = llm
        self.prompt_template = hub.pull("rlm/rag-prompt")
        self.vector_store = InMemoryVectorStore(embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.graph = StateGraph(State).add_sequence([self.retrieve_context, self.generate_response]).add_edge(START, "retrieve_context").compile()

    # Convert raw text to Document format
    def text_to_document(self, text):
        return Document(page_content=text, metadata={"source": "user_input"})

    # Store documents in vector database after splitting
    def store_documents(self, documents):
        all_splits = self.text_splitter.split_documents(documents)
        self.vector_store.add_documents(documents=all_splits)

    # Node 1: Retrieve relevant documents based on a query. Output = Document[]
    def retrieve_context(self, state: State):
        retrieved_docs = self.vector_store.similarity_search(state["question"], k = 2)
        return {"context": retrieved_docs}
    
    # Node 2: Generate response based on question and context
    def generate_response(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = self.prompt_template.invoke({"question": state["question"], "context": docs_content})
        response = self.llm.invoke(messages)
        return {"answer": response.content}

    # Execute the graph pipeline with a given state
    def invoke_conversation(self, state: State):
        result = self.graph.invoke(state)
        return {"context": result['context'], "answer": result['answer']}