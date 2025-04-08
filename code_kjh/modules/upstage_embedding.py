import requests
import time
from typing import List
from langchain.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

class UpstageEmbeddings(Embeddings):
    def __init__(self, api_key: str, api_url: str, batch_size: int = 64):
        self.api_key = api_key
        self.api_url = api_url
        self.batch_size = batch_size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            payload = {"input": batch, "model": "embedding-query"}
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            all_embeddings.extend([item["embedding"] for item in result["data"]])
            time.sleep(0.1)
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

def save_faiss_index(documents, embedding, index_path="faiss_index"):
    db = FAISS.from_documents(documents, embedding)
    db.save_local(index_path)
