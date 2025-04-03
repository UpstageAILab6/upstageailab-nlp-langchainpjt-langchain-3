import requests
import pandas as pd

def fetch_to_pd(url: str, encoded_key: str, per_page: int = 1000, verbose: bool = True) -> pd.DataFrame:
    """
    전체 데이터를 수집하여 pandas DataFrame으로 반환합니다.
    """


    headers = {"accept": "*/*"}
    page = 1
    all_data = []

    if verbose:
        print(f"📦 전체 데이터 수집 시작: {url}")

    while True:
        full_url = f"{url}?page={page}&perPage={per_page}&serviceKey={encoded_key}"
        if verbose:
            print(f"📄 페이지 {page} 요청 중...")

        response = requests.get(full_url, headers=headers)
        if response.status_code != 200:
            print("❌ 요청 실패:", response.status_code)
            break

        try:
            json_data = response.json()
        except Exception as e:
            print("❌ JSON 파싱 오류:", e)
            break

        data = json_data.get("data", [])
        if not data:
            if verbose:
                print("✅ 마지막 페이지 도달 또는 데이터 없음")
            break

        all_data.extend(data)
        page += 1

    df = pd.DataFrame(all_data)
    if verbose:
        print(f"✅ 총 {len(df)}건 수집 완료")
    return df
