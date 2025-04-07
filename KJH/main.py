import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS

from data_pipeline.gov24_data_pipeline import run_gov24_data_pipeline
from modules.data_loader import detect_changes, convert_to_documents
from modules.chunk_splitter import split_by_char, split_by_token
from modules.upstage_embedding import UpstageEmbeddings
from modules.llm_prompt import make_prompt, query_solar
# path 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # c:\Users\jihu6\code\RAG\KJH 
DATA_PATH = os.path.join(BASE_DIR, "data", "combined_service_data_merged.json")
PREV_PATH = os.path.join(BASE_DIR, "data", "combined_service_data_merged_prev.json")

# 환경변수 가져오기
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

GOV24_API_KEY=os.getenv("GOV24_API_KEY")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
UPSTAGE_API_URL = os.getenv("UPSTAGE_API_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# data_pipeline 실행
run_gov24_data_pipeline()

# 🔹 JSON 로드 (new)
with open(DATA_PATH, "r", encoding="utf-8") as f:
    new_data = json.load(f)
new_dict = {item["서비스ID"]: item for item in new_data}

# 🔹 JSON 로드 (prev)
if os.path.exists(PREV_PATH):
    with open(PREV_PATH, "r", encoding="utf-8") as f:
        prev_data = json.load(f)
    prev_dict = {item["서비스ID"]: item for item in prev_data}
else:
    prev_data = []
    prev_dict = {}

# data 변환 확인
added, updated, deleted = detect_changes(new_data=new_data, prev_data=prev_data)
# 임베딩 객체 생성
embedding = UpstageEmbeddings(api_key=UPSTAGE_API_KEY,api_url=UPSTAGE_API_URL,batch_size=64)

if added or updated or deleted:
    print("임베딩 업데이트 필요\n")
    print(len(added),len(updated),len(deleted))
    documents = convert_to_documents(new_data)
    # 청크 분할
    token_split_docs = split_by_token(documents=documents)

    # FAISS 인덱스 생성 및 저장
    db = FAISS.from_documents(token_split_docs, embedding)  # 문서 임베딩 후 FAISS 인덱스 생성
    db.save_local("faiss_index")  # 인덱스를 로컬 디렉토리에 저장
else:
    print("수정사항이 없어 임베딩 과정을 건너 뛰었습니다.")

# ✅ allow_dangerous_deserialization=True 추가
db = FAISS.load_local(
    "faiss_index",
    embeddings=embedding,
    allow_dangerous_deserialization=True  # ✅ Pickle 로드 허용
)

# 질문 입력 받기
query = input("💬 질문을 입력하세요: ")

# 유사한 문서 찾기
docs = db.similarity_search(query, k=3)

2# 🔍 유사 문서 + 조건 출력
for i, doc in enumerate(docs):
    print(f"📄 문서 {i+1}")
    # 🔸 문서 요약 (앞부분만 출력)
    print(doc.page_content[:500])
    # 🔸 조건 정보 출력
    조건들 = doc.metadata.get("조건", {})
    선택된_조건 = [k for k, v in 조건들.items() if v]    
    print(f"📌 조건 태그: {', '.join(선택된_조건) if 선택된_조건 else '조건 없음'}")
    print("-" * 50)

# prompt 불러오기
prompt = make_prompt(retrieved_docs=docs, query=query)

# LLM을 이용해 문서 찾기
print(query_solar(prompt=prompt, api_key=UPSTAGE_API_KEY))
