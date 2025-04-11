import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer

class SemanticSearch:
    def __init__(self, index_path="faiss_index.index", chunks_path="chunks.pkl"):
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.chunks = []

    def create_index(self, texts):
        self.chunks = [t for t in texts if len(t.strip()) > 40]
        embeddings = self.model.encode(self.chunks, convert_to_numpy=True)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        self.save_index()

    def save_index(self):
        if self.index:
            faiss.write_index(self.index, self.index_path)
        with open(self.chunks_path, "wb") as f:
            pickle.dump(self.chunks, f)

    def load_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.chunks_path, "rb") as f:
                self.chunks = pickle.load(f)
        else:
            raise FileNotFoundError("FAISS index or chunk file not found. Please build the index first.")

    def search(self, query, top_k=3):
        if self.index is None or not self.chunks:
            raise ValueError("Index is not loaded. Call load_index() first.")
        
        query_vec = self.model.encode([query])
        distances, indices = self.index.search(query_vec, top_k)
        results = [(self.chunks[i], distances[0][j]) for j, i in enumerate(indices[0]) if i < len(self.chunks)]
        return results
