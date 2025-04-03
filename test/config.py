import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 검증
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일에 설정하거나 환경 변수로 설정하세요.")

# LangSmith 설정 (선택 사항)
ENABLE_LANGSMITH = os.getenv("ENABLE_LANGSMITH", "false").lower() == "true"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "test-RAG")

# 모델 설정
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0"))

# 문서 분할 설정
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "1000"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "50"))

# 벡터 스토어 설정
DEFAULT_VECTOR_STORE_PATH = os.getenv("DEFAULT_VECTOR_STORE_PATH", "faiss_index")