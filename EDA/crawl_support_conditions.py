from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# 셀레니움 옵션 설정
options = Options()
options.add_argument("--headless")  # 브라우저를 띄우지 않고 실행
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 크롬 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 대상 페이지 접속
url = "https://www.data.go.kr/data/15113968/openapi.do#/"
driver.get(url)
time.sleep(3)  # 페이지 로딩 대기

# 버튼 클릭을 통해 접혀있는 항목 모두 펼치기 (최대 10회 시도)
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

# 현재 파이썬 파일 기준으로 data 폴더 생성
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# CSV 파일로 저장
save_path = os.path.join(DATA_DIR, "supportConditions_model.csv")
df = pd.DataFrame(data)
df.to_csv(save_path, index=False, encoding="utf-8-sig")

print(f"supportConditions_model.csv 파일 저장 완료: {save_path}")

# 드라이버 종료
driver.quit()
