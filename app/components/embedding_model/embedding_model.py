import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer


class EmbeddingModel:
    def __init__(self, backend="mini-lm"):
        self.backend = backend

        if backend == "mini-lm":
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        elif backend == "distilbert":
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            self.model = AutoModel.from_pretrained("distilbert-base-uncased")
        else:
            raise ValueError("Unsupported backend")

    def encode(self, text):
        if self.backend == "mini-lm":
            return self.model.encode(text, convert_to_tensor=True)
        elif self.backend == "distilbert":
            inputs = self.tokenizer(
                text, return_tensors="pt", truncation=True, padding=True
            )
            with torch.no_grad():
                outputs = self.model(**inputs)
            # Mean pooling over token embeddings
            last_hidden = outputs.last_hidden_state  # [1, seq_len, hidden_dim]
            mask = inputs["attention_mask"].unsqueeze(-1)
            pooled = (last_hidden * mask).sum(1) / mask.sum(1)
            return pooled.squeeze().cpu()  # return 1D tensor

    # Embed list of documents. Compatbility function for langchain's InMemoryVectorStore
    def embed_documents(self, texts):
        return [self.encode(text).tolist() for text in texts]

    # Embed user query. Compatbility function for langchain's InMemoryVectorStore
    def embed_query(self, query):
        encoded_query = self.encode(query)
        return encoded_query.tolist()
