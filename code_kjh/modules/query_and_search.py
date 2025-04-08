from langchain.vectorstores import FAISS

def load_faiss_index(embedding, path="faiss_index"):
    return FAISS.load_local(path, embeddings=embedding, allow_dangerous_deserialization=True)

def search_similar_documents(db, query, k=3):
    docs = db.similarity_search(query, k=k)
    return docs
