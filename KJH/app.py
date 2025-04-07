import os
import json
import streamlit as st
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS

from modules.data_loader import detect_changes, convert_to_documents
from modules.chunk_splitter import split_by_token
from modules.upstage_embedding import UpstageEmbeddings
from modules.llm_prompt import make_prompt, query_solar

# 📁 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "combined_service_data_merged.json")
PREV_PATH = os.path.join(BASE_DIR, "data", "combined_service_data_merged_prev.json")
INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")
INDEX_FILE = os.path.join(INDEX_DIR, "index.faiss")

# 🔐 환경변수 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
UPSTAGE_API_URL = os.getenv("UPSTAGE_API_URL")

# 🌐 Streamlit UI
st.set_page_config(page_title="정부지원 서비스 질문", page_icon="📝")
st.title("📚 정부지원 서비스 RAG 데모")

# ✅ 벡터 DB 초기화 (캐시 사용)
@st.cache_resource
def load_db():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        new_data = json.load(f)

    if os.path.exists(PREV_PATH):
        with open(PREV_PATH, "r", encoding="utf-8") as f:
            prev_data = json.load(f)
    else:
        prev_data = []

    added, updated, deleted = detect_changes(new_data=new_data, prev_data=prev_data)
    embedding = UpstageEmbeddings(api_key=UPSTAGE_API_KEY, api_url=UPSTAGE_API_URL)

    if added or updated or deleted or not os.path.exists(INDEX_FILE):
        documents = convert_to_documents(new_data)
        split_docs = split_by_token(documents)
        db = FAISS.from_documents(split_docs, embedding)
        db.save_local(INDEX_DIR)
    else:
        db = FAISS.load_local(INDEX_DIR, embeddings=embedding, allow_dangerous_deserialization=True)

    return db

# 🔹 벡터 DB 로딩
db = load_db()

# 🔍 질문 입력
query = st.text_input("💬 궁금한 점을 입력하세요:", placeholder="예: 25세 여성이 받을 수 있는 주거지원은?")
if query:
    with st.spinner("답변 생성 중..."):
        docs = db.similarity_search(query, k=3)

        for i, doc in enumerate(docs):
            st.markdown(f"### 📄 문서 {i+1}")
            st.code(doc.page_content[:500])
            조건들 = doc.metadata.get("조건", {})
            선택된_조건 = [k for k, v in 조건들.items() if v]
            if 선택된_조건:
                st.markdown("**📌 조건 태그:** " + ", ".join(선택된_조건))

        prompt = make_prompt(retrieved_docs=docs, query=query)
        answer = query_solar(prompt=prompt, api_key=UPSTAGE_API_KEY)

        st.markdown("### 🤖 응답")
        st.success(answer)
