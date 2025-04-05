import os
import urllib.parse
from dotenv import load_dotenv

# ✅ RAG 폴더의 .env를 명시적으로 로드
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # EDA 기준 상위 경로 (RAG)
env_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=env_path)

# ✅ 환경 변수 불러오기
GOV24_API_KEY = os.getenv("GOV24_API_KEY")
if GOV24_API_KEY is None:
    raise ValueError("❌ .env에서 'GOV24_API_KEY'를 찾을 수 없습니다.")

# ✅ URL 인코딩
encoded_key = urllib.parse.quote(GOV24_API_KEY, safe='')

# ✅ 결과 출력
print("✅ 인코딩된 키:", encoded_key[:10] + "...")
