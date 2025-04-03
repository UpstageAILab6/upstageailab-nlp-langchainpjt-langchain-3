from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

def crawl_support_conditions_model(verbose: bool = True) -> pd.DataFrame:
    """
    셀레니움을 이용해 정부24 OpenAPI 문서에서 supportConditions_model 항목 설명을 크롤링합니다.

    Returns:
        pd.DataFrame: 항목코드와 설명이 담긴 DataFrame
    """
    # 셀레니움 옵션 설정
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 드라이버 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://www.data.go.kr/data/15113968/openapi.do#/"
    driver.get(url)
    time.sleep(3)

    # 접혀있는 버튼 클릭 (최대 10회)
    for _ in range(10):
        buttons = driver.find_elements(By.CSS_SELECTOR, "div#model-supportConditions_model button.model-box-control[aria-expanded='false']")
        if not buttons:
            break
        for btn in buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.05)
            except:
                continue

    # HTML 파싱
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("div#model-supportConditions_model table.model tr.property-row")

    # 항목코드와 설명 추출
    data = []
    for row in rows:
        tds = row.find_all("td")
        if len(tds) == 2:
            code = tds[0].get_text(strip=True)
            desc_div = tds[1].find("div", class_="markdown")
            if desc_div:
                desc = desc_div.get_text(strip=True)
                data.append({"항목코드": code, "설명": desc})

    # 드라이버 종료
    driver.quit()

    df = pd.DataFrame(data)
    if verbose:
        print(f"✅ 크롤링 완료: {len(df)}개 항목 수집됨")

    return df
