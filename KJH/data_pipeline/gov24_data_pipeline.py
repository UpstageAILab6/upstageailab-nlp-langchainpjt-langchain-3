import os  # 운영체제 관련 기능 제공 (경로 등)
import urllib.parse  # URL 인코딩을 위한 모듈
import pandas as pd  # 데이터프레임 사용
import shutil  # 파일 복사 등
from collections import defaultdict, Counter
from dotenv import load_dotenv  # .env 파일 로드
from gov24_api_fetcher import fetch_to_pd  # API 요청 함수
from support_model_crawler import crawl_support_conditions_model  # 조건 설명 크롤링 함수

# ---------------------------
# 🔧 1. .env 로딩 및 API 키 인코딩
# ---------------------------

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # EDA 기준 상위 경로 (KJH)
env_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=env_path)

GOV24_API_KEY = os.getenv("GOV24_API_KEY")  # GOV24_API_KEY 환경 변수 로드
if GOV24_API_KEY is None:  # 환경 변수 없을 시 예외 처리
    raise ValueError("❌ .env에서 'GOV24_API_KEY'를 찾을 수 없습니다.")

encoded_key = urllib.parse.quote(GOV24_API_KEY, safe='')  # URL 인코딩된 API 키 생성

# ---------------------------
# 📁 2. 경로 설정
# ---------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # EDA 기준 상위 경로 (KJH)
DATA_DIR = os.path.join(BASE_DIR, "data")  # 데이터 저장 폴더 경로
os.makedirs(DATA_DIR, exist_ok=True)  # 데이터 폴더 없으면 생성

DETAIL_FILENAME = "serviceDetail_all"
CONDITIONS_FILENAME = "supportConditions_all"
MODEL_FILENAME = "supportConditions_model"



detail_json_path = os.path.join(DATA_DIR, f"{DETAIL_FILENAME}.json")
conditions_json_path = os.path.join(DATA_DIR, f"{CONDITIONS_FILENAME}.json")
model_json_path = os.path.join(DATA_DIR, f"{MODEL_FILENAME}.json")
combined_json_path = os.path.join(DATA_DIR, "combined_service_data.json")
merged_json_path = os.path.join(DATA_DIR, "combined_service_data_merged.json")

# ---------------------------
# 🛟 3. 기존 JSON 백업 함수
# ---------------------------
def backup_if_exists(src_path: str, backup_name: str):
    if os.path.exists(src_path):
        backup_path = os.path.join(DATA_DIR, f"{backup_name}_prev.json")
        shutil.copy(src_path, backup_path)
        print(f"📦 백업 완료: {backup_path}")

# ---------------------------
# 📥 4. 데이터 수집
# ---------------------------
detail_df = fetch_to_pd("https://api.odcloud.kr/api/gov24/v3/serviceDetail", encoded_key)
conditions_df = fetch_to_pd("https://api.odcloud.kr/api/gov24/v3/supportConditions", encoded_key)
model_df = crawl_support_conditions_model()

# ---------------------------
# 🔤 5. 항목코드 → 설명 매핑 및 중복 처리
# ---------------------------
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

# ---------------------------
# 🧹 6. 중복 설명 컬럼 통합
# ---------------------------
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

# ---------------------------
# 🛠️ 7. 조건 필드 가공
# ---------------------------
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

# ---------------------------
# 🔗 8. detail_df와 병합
# ---------------------------
combined_df = pd.merge(
    detail_df,
    conditions_df[["서비스명", "대상연령", "조건"]],
    on="서비스명",
    how="inner"
)

# ---------------------------
# 📚 9. combined_df에서 서비스명 기준 병합 정보 저장
# ---------------------------
from copy import deepcopy

merged_rows = []
for name, group in combined_df.groupby("서비스명"):
    base = deepcopy(group.iloc[0].to_dict())
    for _, row in group.iloc[1:].iterrows():
        for col, val in row.items():
            base_val = base.get(col)
            if isinstance(base_val, str) and isinstance(val, str) and base_val != val:
                base[col] = "||".join(sorted(set(base_val.split("||") + val.split("||"))))
            elif isinstance(base_val, list) and isinstance(val, list):
                base[col] = list(set(base_val) | set(val))
            elif isinstance(base_val, dict) and isinstance(val, dict):
                merged = {}
                for k in set(base_val) | set(val):
                    v1 = base_val.get(k)
                    v2 = val.get(k)
                    merged[k] = v1 if v1 is not None else v2
                base[col] = merged
            elif pd.isna(base_val) and pd.notna(val):
                base[col] = val
            elif base_val != val:
                base[col] = f"{base_val}||{val}"
    merged_rows.append(base)

combined_merged_df = pd.DataFrame(merged_rows)


# ---------------------------
# 💾 10. 저장 전 백업
# ---------------------------
backup_if_exists(detail_json_path, DETAIL_FILENAME)
backup_if_exists(conditions_json_path, CONDITIONS_FILENAME)
backup_if_exists(model_json_path, MODEL_FILENAME)
backup_if_exists(combined_json_path, "combined_service_data")
backup_if_exists(merged_json_path, "combined_service_data_merged")

# ---------------------------
# 📤 11. JSON 저장
# ---------------------------
detail_df.to_json(detail_json_path, orient="records", force_ascii=False, indent=2)
conditions_df.to_json(conditions_json_path, orient="records", force_ascii=False, indent=2)
model_df.to_json(model_json_path, orient="records", force_ascii=False, indent=2)
combined_df.to_json(combined_json_path, orient="records", force_ascii=False, indent=2)
combined_merged_df.to_json(merged_json_path, orient="records", force_ascii=False, indent=2)


print(f"✅ JSON 저장 완료: {detail_json_path}")
print(f"✅ JSON 저장 완료: {conditions_json_path}")
print(f"✅ JSON 저장 완료: {model_json_path}")
print(f"✅ 병합 JSON 저장 완료: {combined_json_path}")
print(f"✅ 병합된 combined_df 저장 완료: {merged_json_path}")
print(f"🔁 병합 전: {len(combined_df)} / 병합 후: {len(combined_merged_df)}")