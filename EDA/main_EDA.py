import os
import urllib.parse
import pandas as pd
from collections import defaultdict, Counter
from gov24_api_fetcher import fetch_to_pd
from support_model_crawler import crawl_support_conditions_model

# 1. Encode API Key
raw_key = "wjb1j9pPgWVcb3MZXs8UmzxiAROp/RvAPf0sAqfZ0drTEC+yeMEYSl3znaUqUi/guGON1tqmADfodOIZ9y7F/w=="
encoded_key = urllib.parse.quote(raw_key, safe='')

# 2. Path Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DETAIL_FILENAME = "serviceDetail_all"
CONDITIONS_FILENAME = "supportConditions_all"
MODEL_FILENAME = "supportConditions_model"

detail_json_path = os.path.join(DATA_DIR, f"{DETAIL_FILENAME}.json")
conditions_json_path = os.path.join(DATA_DIR, f"{CONDITIONS_FILENAME}.json")
model_json_path = os.path.join(DATA_DIR, f"{MODEL_FILENAME}.json")
combined_json_path = os.path.join(DATA_DIR, "combined_service_data.json")

# 3. Fetch Data
detail_df = fetch_to_pd("https://api.odcloud.kr/api/gov24/v3/serviceDetail", encoded_key)
conditions_df = fetch_to_pd("https://api.odcloud.kr/api/gov24/v3/supportConditions", encoded_key)
model_df = crawl_support_conditions_model()

# 4. 항목코드 → 설명 매핑 및 중복 처리
code_to_desc = dict(zip(model_df["항목코드"], model_df["설명"]))

desc_counter = Counter()
new_columns = []
for col in conditions_df.columns:
    desc = code_to_desc.get(col, col)
    desc_counter[desc] += 1
    if desc_counter[desc] > 1:
        desc = f"{desc}_{desc_counter[desc]}"
    new_columns.append(desc)

conditions_df.columns = new_columns
print("✅ supportConditions_df column names mapped to description")

# 5. 중복 설명 컬럼 통합
merged_df = pd.DataFrame(index=conditions_df.index)
column_groups = defaultdict(list)
for col in conditions_df.columns:
    base_name = col.split("_")[0]
    column_groups[base_name].append(col)

for base_name, col_list in column_groups.items():
    merged_series = conditions_df[col_list[0]]
    for other_col in col_list[1:]:
        merged_series = merged_series.combine_first(conditions_df[other_col])
    merged_df[base_name] = merged_series

conditions_df = merged_df
print("✅ Duplicate description columns merged")

# 6. 조건 필드 가공
exclude_condition_cols = ["서비스명", "대상연령(시작)", "대상연령(종료)"]
condition_cols = [col for col in conditions_df.columns if col not in exclude_condition_cols]

conditions_df["조건"] = conditions_df.apply(
    lambda row: {
        col: True for col in condition_cols if str(row[col]).strip().upper() == "Y"
    },
    axis=1
)

conditions_df["대상연령"] = conditions_df.apply(
    lambda row: {
        "시작": int(row["대상연령(시작)"]) if pd.notnull(row["대상연령(시작)"]) else None,
        "종료": int(row["대상연령(종료)"]) if pd.notnull(row["대상연령(종료)"]) else None,
    },
    axis=1
)

# 7. 병합 (서비스명 기준)
combined_df = pd.merge(
    detail_df,
    conditions_df[["서비스명", "대상연령", "조건"]],
    on="서비스명",
    how="inner"
)

# 8. 저장
detail_df.to_json(detail_json_path, orient="records", force_ascii=False, indent=2)
conditions_df.to_json(conditions_json_path, orient="records", force_ascii=False, indent=2)
model_df.to_json(model_json_path, orient="records", force_ascii=False, indent=2)
combined_df.to_json(combined_json_path, orient="records", force_ascii=False, indent=2)

print(f"✅ JSON 저장 완료: {detail_json_path}")
print(f"✅ JSON 저장 완료: {conditions_json_path}")
print(f"✅ JSON 저장 완료: {model_json_path}")
print(f"✅ 병합 JSON 저장 완료: {combined_json_path}")
