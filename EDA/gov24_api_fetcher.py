import requests
import pandas as pd
import time

def fetch_to_pd(
    url: str,
    encoded_key: str,
    per_page: int = 500,
    verbose: bool = True,
    page_retry_limit: int = 3
) -> pd.DataFrame:
    """
    페이지 단위로 재시도하면서 전체 데이터를 수집합니다.
    """
    
    headers = {"accept": "*/*"}
    page = 1
    all_data = []

    if verbose:
        print(f"📦 전체 데이터 수집 시작: {url}")

    while True:
        full_url = f"{url}?page={page}&perPage={per_page}&serviceKey={encoded_key}"
        retry_count = 0

        while retry_count < page_retry_limit:
            if verbose:
                print(f"📄 페이지 {page} 요청 중... (재시도 {retry_count + 1}/{page_retry_limit})")

            response = requests.get(full_url, headers=headers)

            if response.status_code == 200:
                try:
                    json_data = response.json()
                    data = json_data.get("data", [])
                    if not data:
                        if verbose:
                            print("✅ 마지막 페이지 도달 또는 데이터 없음")
                        return pd.DataFrame(all_data)
                    all_data.extend(data)
                    page += 1
                    break  # 현재 페이지 성공 → 다음 페이지로
                except Exception as e:
                    print("❌ JSON 파싱 오류:", e)
            else:
                print(f"❌ 요청 실패 (페이지 {page}): {response.status_code}")

            retry_count += 1
            time.sleep(2)

        if retry_count == page_retry_limit:
            print(f"🚫 페이지 {page} 요청 재시도 초과. 중단합니다.")
            break

    return pd.DataFrame(all_data)
