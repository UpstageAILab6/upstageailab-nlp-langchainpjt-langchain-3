import os
import urllib.parse
import pandas as pd
from collections import defaultdict
from gov24_api_fetcher import fetch_to_pd
from support_model_crawler import crawl_support_conditions_model

# 1. API 키 인코딩
raw_key = "wjb1j9pPgWVcb3MZXs8UmzxiAROp/RvAPf0sAqfZ0drTEC+yeMEYSl3znaUqUi/guGON1tqmADfodOIZ9y7F/w=="
encoded_key = urllib.parse.quote(raw_key, safe='')

# 2. 저장 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

Detail_csv_path = os.path.join(DATA_DIR, "serviceDetail_all.csv")
Conditions_csv_path = os.path.join(DATA_DIR, "supportConditions_all.csv")
Conditions_model_csv_path = os.path.join(DATA_DIR, "supportConditions_model.csv")

# 3. 데이터 수집
serviceDetail_df = fetch_to_pd(
    url="https://api.odcloud.kr/api/gov24/v3/serviceDetail",
    encoded_key=encoded_key
)
supportConditions_df = fetch_to_pd(
    url="https://api.odcloud.kr/api/gov24/v3/supportConditions",
    encoded_key=encoded_key
)
supportconditions_model_df = crawl_support_conditions_model()

# 4. 항목코드 → 설명 매핑 (중복 설명 처리)
from collections import Counter

code_to_desc = dict(zip(
    supportconditions_model_df["항목코드"],
    supportconditions_model_df["설명"]
))

# 설명 중복 시 접미사 추가 (예: 성별, 성별_2)
desc_counter = Counter()
new_columns = []
for col in supportConditions_df.columns:
    desc = code_to_desc.get(col, col)
    desc_counter[desc] += 1
    if desc_counter[desc] > 1:
        desc = f"{desc}_{desc_counter[desc]}"
    new_columns.append(desc)

supportConditions_df.columns = new_columns
print("✅ supportConditions_df 컬럼명이 설명(중복 대응)으로 대체되었습니다.")

# 5. 중복된 설명 통합 (NaN 우선)
merged_df = pd.DataFrame(index=supportConditions_df.index)
column_groups = defaultdict(list)

# base 설명 기준 그룹핑 (성별, 성별_2 → 성별)
for col in supportConditions_df.columns:
    base_name = col.split("_")[0]
    column_groups[base_name].append(col)

# 그룹별 통합
for base_name, col_list in column_groups.items():
    merged_series = supportConditions_df[col_list[0]]
    for other_col in col_list[1:]:
        merged_series = merged_series.combine_first(supportConditions_df[other_col])
    merged_df[base_name] = merged_series

supportConditions_df = merged_df
print("✅ 중복된 설명 컬럼 통합 완료 (NaN 아닌 값 우선)")

# 6. CSV 저장
serviceDetail_df.to_csv(Detail_csv_path, index=False, encoding="utf-8-sig")
print(f"✅ CSV 저장 완료: {Detail_csv_path}")
supportConditions_df.to_csv(Conditions_csv_path, index=False, encoding="utf-8-sig")
print(f"✅ CSV 저장 완료: {Conditions_csv_path}")
