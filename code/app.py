import streamlit as st
import pandas as pd
from config import ConfigLoader
from loader import DocumentLoader
from vectorstore import VectorStoreManager
from llm import GovPolicyLLM
from prompt import GovPolicyPrompt, MarkdownFormatter
from gov_policy_qa import GovPolicyQA
from chat_history import ChatHistory
from logger import Logger
from grounding_checker import VectorstoreGroundingChecker
from langchain_openai import OpenAIEmbeddings

# 페이지 설정
st.set_page_config(page_title="정부 정책 챗봇", layout="wide")
st.title("🇰🇷 정부 지원 정책 질문 챗봇")

# 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatHistory()

if "qa_system" not in st.session_state:
    config = ConfigLoader(project_name="GovPolicyQA")
    config.load()

    st.session_state.logger = Logger()

    doc_loader = DocumentLoader(filepath="data/serviceDetail_all.csv")
    documents = doc_loader.load_documents()

    embeddings = OpenAIEmbeddings()
    vs_manager = VectorStoreManager(embeddings=embeddings)
    vectorstore = vs_manager.load_or_create(documents, path="code/faiss_index_v2")

    llm = GovPolicyLLM(model_name="gpt-4o", temperature=0).get_llm()
    prompt = GovPolicyPrompt().get_prompt()
    formatter = MarkdownFormatter()

    st.session_state.qa_system = GovPolicyQA(vectorstore, embeddings, llm, prompt, formatter)
    st.session_state.grounding_checker = VectorstoreGroundingChecker(vectorstore, embeddings)

# 사용자 질문 입력
user_input = st.text_input("정부 지원 정책에 대해 궁금한 점을 입력하세요", "")

if user_input:
    st.session_state.logger.log_user_input(user_input)
    st.session_state.chat_history.add_user_message(user_input)

    with st.spinner("답변을 생성 중입니다..."):
        answer = st.session_state.qa_system.run(user_input)

    # 🔍 그라운드체킹 실행
    grounding_results = st.session_state.grounding_checker.run(answer)
    grounded_count = sum(r["grounded"] for r in grounding_results)
    total_count = len(grounding_results)

    # 📌 답변 출력
    st.markdown("---")
    st.subheader("📌 답변")
    st.markdown(answer, unsafe_allow_html=True)

    # ✅ 그라운드체킹 한 줄 요약
    if total_count > 0:
        ratio = grounded_count / total_count * 100
        st.markdown(
            f"🧠 **[그라운드체킹 요약]** 총 {total_count}개 문장 중 {grounded_count}개 문장이 문서 기반 정보와 일치합니다. "
            f"(**정확도: {ratio:.1f}%**)"
        )
    else:
        st.markdown("⚠️ **[그라운드체킹 요약]** 문장 기반 검증 결과가 없습니다.")

    # 🧾 문장-근거 매핑 테이블
    st.markdown("---")
    st.subheader("🧾 문장별 유사도 및 근거 문서 매핑 결과")
    if grounding_results:
        df = pd.DataFrame(grounding_results)
        df_display = df[["sentence", "matched_context", "similarity", "grounded"]]
        df_display["similarity"] = df_display["similarity"].apply(lambda x: round(x, 3))
        df_display["grounded"] = df_display["grounded"].apply(lambda x: "✅" if x else "❌")
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("표시할 항목이 없습니다.")

    st.session_state.logger.log_assistant_response(answer)
    st.session_state.chat_history.add_assistant_message(answer)

# 💬 대화 히스토리
if st.session_state.chat_history.get_history():
    st.markdown("---")
    st.subheader("💬 대화 기록")
    for message in st.session_state.chat_history.get_history():
        role = message["role"]
        content = message["content"]
        if role == "user":
            st.markdown(f"**👤 사용자:** {content}")
        elif role == "assistant":
            st.markdown(f"**🤖 챗봇:**\n\n{content}", unsafe_allow_html=True)