# 🔧 .env 환경 변수 설정 가이드

이 프로젝트에서는 API 키와 설정 값을 외부에 노출하지 않기 위해 `.env` 파일을 사용합니다.  
아래 예시를 참고하여 루트 디렉토리에 `.env` 파일을 생성하고 각 항목을 설정하세요.

> ⚠️ `.env` 파일은 **절대 깃허브 등에 공개되지 않도록 주의하세요!**  
> `.gitignore`에 반드시 포함되어야 합니다.

📌 `.env` 파일은 **프로젝트 최상위 폴더**에 위치해야 합니다.  
📌 아래 기본 구조를 복사해 `.env` 파일에 붙여 넣고, **API 키 부분만 개인 키로 변경**하세요.

---

## ✅ 1. 기본 구조 예시

```env
# 🔐 GOV24 오픈API 키
GOV24_API_KEY=발급받은_API_키

# 🔐 Solar API 키 (Upstage에서 받은 키)
UPSTAGE_API_KEY=up_로_시작하는_키
UPSTAGE_API_URL=https://api.upstage.ai/v1/embeddings

# 🔐 OpenAI API 키 (사용 시에만)
OPENAI_API_KEY=sk-로_시작하는_키

# 🔐 LangSmith 키 (LangChain 실험 기록용)
LANGSMITH_API_KEY=lsv2_로_시작하는_키
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# ✅ 프로젝트 이름 (LangSmith에서 프로젝트 구분용)
LANGCHAIN_PROJECT=프로젝트_이름
