# data_pipeline/gov24_data_pipeline.py
import os
import urllib.parse
import pandas as pd
import shutil
from collections import defaultdict, Counter
from dotenv import load_dotenv
from copy import deepcopy
from data_pipeline.gov24_api_fetcher import fetch_to_pd
from data_pipeline.support_model_crawler import crawl_support_conditions_model

def run_gov24_data_pipeline():
    # 1. 환경변수 및 경로 설정
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(base_dir, ".env")
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("GOV24_API_KEY")
    if api_key is None:
        raise ValueError("❌ .env에서 'GOV24_API_KEY'를 찾을 수 없습니다.")

    encoded_key = urllib.parse.quote(api_key, safe='')
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    detail_json_path = os.path.join(data_dir, "serviceDetail_all.json")
    conditions_json_path = os.path.join(data_dir, "supportConditions_all.json")
    model_json_path = os.path.join(data_dir, "supportConditions_model.json")
    combined_json_path = os.path.join(data_dir, "combined_service_data.json")
    merged_json_path = os.path.join(data_dir, "combined_service_data_merged.json")

    def backup_if_exists(src_path: str, backup_name: str):
        if os.path.exists(src_path):
            backup_path = os.path.join(data_dir, f"{backup_name}_prev.json")
            shutil.copy(src_path, backup_path)

    # 2. 데이터 수집
    detail_df = fetch_to_pd("https://api.odcloud.kr/api/gov24/v3/serviceDetail", encoded_key)
    conditions_df = fetch_to_pd("https://api.odcloud.kr/api/gov24/v3/supportConditions", encoded_key)
    model_df = crawl_support_conditions_model()

    # 3. 컬럼 매핑 및 통합
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

    # 4. 조건 필드 가공
    exclude_cols = ["서비스명", "대상연령(시작)", "대상연령(종료)"]
    condition_cols = [col for col in conditions_df.columns if col not in exclude_cols]
    conditions_df["조건"] = conditions_df.apply(
        lambda row: {col: True for col in condition_cols if str(row[col]).strip().upper() == "Y"}, axis=1
    )
    conditions_df["대상연령"] = conditions_df.apply(
        lambda row: {
            "시작": int(row["대상연령(시작)"]) if pd.notnull(row["대상연령(시작)"]) else None,
            "종료": int(row["대상연령(종료)"]) if pd.notnull(row["대상연령(종료)"]) else None,
        }, axis=1
    )

    # 5. 병합
    combined_df = pd.merge(detail_df, conditions_df[["서비스명", "대상연령", "조건"]], on="서비스명", how="inner")
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
                    merged = {k: base_val.get(k) if base_val.get(k) is not None else val.get(k)
                              for k in set(base_val) | set(val)}
                    base[col] = merged
                elif pd.isna(base_val) and pd.notna(val):
                    base[col] = val
                elif base_val != val:
                    base[col] = f"{base_val}||{val}"
        merged_rows.append(base)
    combined_merged_df = pd.DataFrame(merged_rows)

    # 6. 저장 및 백업
    backup_if_exists(detail_json_path, "serviceDetail_all")
    backup_if_exists(conditions_json_path, "supportConditions_all")
    backup_if_exists(model_json_path, "supportConditions_model")
    backup_if_exists(combined_json_path, "combined_service_data")
    backup_if_exists(merged_json_path, "combined_service_data_merged")

    detail_df.to_json(detail_json_path, orient="records", force_ascii=False, indent=2)
    conditions_df.to_json(conditions_json_path, orient="records", force_ascii=False, indent=2)
    model_df.to_json(model_json_path, orient="records", force_ascii=False, indent=2)
    combined_df.to_json(combined_json_path, orient="records", force_ascii=False, indent=2)
    combined_merged_df.to_json(merged_json_path, orient="records", force_ascii=False, indent=2)

    print(f"✅ JSON 저장 및 백업 완료")
    print(f"🔁 병합 전: {len(combined_df)} / 병합 후: {len(combined_merged_df)}")