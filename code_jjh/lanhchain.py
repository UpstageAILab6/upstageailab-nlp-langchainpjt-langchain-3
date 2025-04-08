#!/usr/bin/env python
# coding: utf-8




# In[5]:


import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate


# In[6]:


import os
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.tracers import LangChainTracer

# .env 파일 로드
load_dotenv()

# ✅ 환경 변수 불러오기 상태 확인
print("✅ OpenAI 키 로드됨:", os.getenv("OPENAI_API_KEY") is not None)
print("✅ LangSmith 키 로드됨:", os.getenv("LANGSMITH_API_KEY") is not None)

# LangSmith 환경 설정 (동적 설정)
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")  # .env에서 불러옴
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "Test"  # 원하는 프로젝트 이름

# LangSmith 클라이언트 직접 사용할 수도 있음
client = Client()
print("현재 LangSmith 프로젝트:", os.environ["LANGCHAIN_PROJECT"])


# In[7]:


# 1. 절대경로 지정
absolute_path = r"C:\Users\duffp\RAG\upstageailab-nlp-langchainpjt-langchain-3\data\gov24_serviceList_all.json"

# 2. 파일 존재 여부 확인
if os.path.exists(absolute_path):
    print("✅ 파일 경로 확인 완료:", absolute_path)
else:
    print("❌ 경로에 파일이 존재하지 않습니다.")

# 3. JSON 로드 함수에 직접 경로 넘기기
def load_json_from_absolute_path(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"📦 JSON 로드 완료: 항목 수 {len(data)}개")
        return data
    except Exception as e:
        print(f"❌ 파일 로드 오류: {e}")
        return []

# 사용 예시
data = load_json_from_absolute_path(absolute_path)


# In[8]:


from langchain_core.documents import Document

documents = []
for item in data:
    content = f"""
서비스명: {item.get('서비스명')}
서비스목적: {item.get('서비스목적요약')}
지원대상: {item.get('지원대상')}
지원내용: {item.get('지원내용')}
신청방법: {item.get('신청방법')}
신청기한: {item.get('신청기한')}
선정기준: {item.get('선정기준')}
서비스분야: {item.get('서비스분야')}
소관기관: {item.get('소관기관명')}
문의전화: {item.get('전화문의')}
상세조회URL: {item.get('상세조회URL')}
"""
    documents.append(Document(page_content=content.strip(), metadata={"서비스ID": item.get("서비스ID")}))

print(f"LangChain 문서 변환 완료: {len(documents)}개")


# In[9]:


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""]
)


# In[10]:


split_documents = text_splitter.split_documents(documents)
print(f"분할된 문서 수: {len(split_documents)}")
print("첫 청크 내용:\n", split_documents[0].page_content[:500])


# In[15]:


for i, doc in enumerate(split_documents[:3]):
    print(f"\n--- 청크 {i+1} ---")
    print(doc.page_content)


# In[11]:


from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

# 토큰 사용 안 하고 기존 벡터를 로드함
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local("faiss_store", embeddings, allow_dangerous_deserialization=True)


# In[14]:


retriever_sim = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
retriever_mmr = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 10, "lambda_mult": 0.8})


# In[17]:


prompt = PromptTemplate.from_template("""너는 복지 혜택을 추천해주는 챗봇이야.
아래는 사용자 질문과 관련된 혜택 문서들이야."

# Context:
{context}

# Question:
{question}

# Answer:
- 관련된 복지 혜택을 자연스럽고 친절하게 설명해줘
- 대상 조건과 신청 방법도 간단히 알려줘
- 혜택이 여러 개면 순서대로 정리해줘
- 한글로, 부드럽고 공손한 말투로 작성해줘
""")


# In[18]:


# LangSmith 트레이싱은 .env 설정만으로 자동 활성화됨
# LANGSMITH_TRACING=true 설정 시 실행 로그를 LangSmith에서 확인 가능

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)


# In[19]:


chain_sim = (
    {"context": retriever_sim, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

chain_mmr = (
    {"context": retriever_mmr, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# In[ ]:


import streamlit as st

# 제목
st.title("혜택 추천 시스템: Similarity vs MMR")

# 사용자 질문 입력받기
question = st.text_input("질문을 입력해주세요", placeholder="예: 경기도에 거주하는 29살 남자인데 내가 받을 수 있는 혜택이 있을까?")

# 버튼 클릭 시 실행
if st.button("혜택 추천 받기"):
    if question:
        # 유사도 방식 응답
        response_sim = chain_sim.invoke(question)
        # MMR 방식 응답
        response_mmr = chain_mmr.invoke(question)

        # 출력
        st.subheader("🔹 Similarity 방식 응답")
        st.write(response_sim)

        st.subheader("🔸 MMR 방식 응답")
        st.write(response_mmr)
    else:
        st.warning("질문을 입력해주세요.")


# In[24]:


# In[ ]:




