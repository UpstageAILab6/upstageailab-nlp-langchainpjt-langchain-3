import os
import urllib.parse
import pandas as pd
from gov24_api_fetcher import fetch_to_pd

# API key
raw_key = "wjb1j9pPgWVcb3MZXs8UmzxiAROp/RvAPf0sAqfZ0drTEC+yeMEYSl3znaUqUi/guGON1tqmADfodOIZ9y7F/w=="
encoded_key = urllib.parse.quote(raw_key, safe='')

# 저장 경로 설정 (현재 파일 기준)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Detail_csv_path = os.path.join(BASE_DIR, "data", "serviceDetail_all.csv")
Conditions_csv_path = os.path.join(BASE_DIR, "data", "supportConditions_all.csv")
Conditions_model_csv_path = os.path.join(BASE_DIR, "data", "supportConditions_model.csv")

# 디렉토리 없으면 생성
os.makedirs(os.path.dirname(Detail_csv_path), exist_ok=True)
os.makedirs(os.path.dirname(Conditions_csv_path), exist_ok=True)



# serviceDetail df 형태로 가져오기
serviceDetail_df = fetch_to_pd(
    url="https://api.odcloud.kr/api/gov24/v3/serviceDetail",
    encoded_key=encoded_key
)
# 저장
serviceDetail_df.to_csv(Detail_csv_path, index=False, encoding="utf-8-sig")
print(f"✅ CSV 저장 완료: {Detail_csv_path}")




# supportConditions df 형태로 가져오기

supportConditions_df = fetch_to_pd(
    url = "https://api.odcloud.kr/api/gov24/v3/supportConditions",
    encoded_key=encoded_key
)
supportConditions_df.to_csv(Conditions_csv_path, index=False, encoding="utf-8-sig")
print(f"✅ CSV 저장 완료: {Conditions_csv_path}")





from support_model_crawler import crawl_support_conditions_model
# 예시 실행
support_conditions_df = crawl_support_conditions_model()

# 확인
print(support_conditions_df.head())

# 저장이 필요하다면 나중에 CSV로 저장
support_conditions_df.to_csv(Conditions_model_csv_path, index=False, encoding="utf-8-sig")
print(f"✅ CSV 저장 완료: {Conditions_model_csv_path}")
