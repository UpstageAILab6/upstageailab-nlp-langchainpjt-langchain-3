[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/5BS4k7bR)
# **LangChain 프로젝트** *(예시)*

LangChain과 MLOps 기술을 활용하여, 사내 문서 기반 Q&A 시스템을 구축하는 프로젝트입니다.  
RAG(Retrieval-Augmented Generation) 구조를 바탕으로 문서 검색 및 응답 시스템을 구현하고, 전체 모델 생애주기를 관리 가능한 파이프라인으로 구성했습니다.

- **프로젝트 기간:** 2025.03.01 ~ 2025.04.15  
- **주제:** LangChain 기반 문서 검색 + Q&A 자동화 시스템  

---

# **팀원 소개**

| 이름      | 역할             | GitHub                | 담당 기능                                         |
|-----------|------------------|------------------------|--------------------------------------------------|
| **전종훈** | 팀장 / 역할 | [GitHub 링크](#)       | OPEN AI , ChatGpt LLM |
| **심원형** |  역할   | [GitHub 링크](#)       | OPEN AI , ChatGpt LLM  |
| **김지후** | 역할 | [GitHub 링크](#)       | 데이터 수집, 전처리, solar LLM           |
| **천창현** | 역할     | [GitHub 링크](#)       | OPEN AI , ChatGpt LLM         |

---

# **파이프라인 워크플로우**

RAG를 활용한 혜택 추천 챗봇 (BenePick)

## **1. 비즈니스 문제 정의**
- 나에게 맞는 혜택을 받아볼 수 있는 앱, 채널 구축

## **2. 데이터 수집 및 전처리**
1. **데이터 수집**
    - 정부24 OpenAPI 호출
   (https://www.data.go.kr/data/15113968/openapi.do#/)
   - 지원조건 항목 코드 크롤링
   - 항목 설명 매핑 및 중복 컬럼 통합
   - 조건 및 연령 필드 가공
   - 서비스명 기준 병합 처리
   - `.json` 형태로 저장
   - 저장 전 기존 `.json` 파일은 `_prev.json` 형식으로 백업
2. **전처리**
   - LangChain의 DocumentLoader 사용
   - Chunking
   - Target 지정
   - Code 값 데이터 변환
3. **임베딩 및 벡터화**
   - OpenAI / ChatGPT 모델 사용
   - SOLAR / SOLAR 모델 사용
   - FAISS / 을 활용한 벡터 DB 구축
4. **데이터 버전 관리**
   - JSON 파일로 데이터 버전 관리

## **3. LLM 및 RAG 파이프라인 구성**
- LangChain의 RetrievalQA 모듈 활용
- Chain 구성: Embedding → Retriever → LLM(응답)
- LLM: OpenAI GPT-4 / Mistral / Claude 등 선택 가능

## **4. 모델 학습 및 실험 추적**
- 필요 시, 사내 문서로 파인튜닝된 LLM 학습
- MLflow를 통해 실험, 하이퍼파라미터, 모델 버전 관리
- Optuna / Weights & Biases 연동 가능

## **5. 실행 환경 구성**
1. **FastAPI 기반 API 서버 구성 (옵션)**
2. **Docker로 로컬 환경에서 통합 실행 가능**
3. **터미널 기반 CLI로 즉시 테스트 가능**
4. **로컬 또는 클라우드 환경(AWS EC2 등) 모두 지원**

## **6. 모니터링 및 재학습 루프**
1. **모델 성능 모니터링**
   - Prometheus, Grafana를 통한 응답 시간 및 정확도 트래킹
2. **데이터 Drift 탐지**
   - Evidently AI 활용
3. **사용자 피드백 루프**
   - 사용자의 thumbs-up/down 기록을 통해 성능 개선
   - 재학습 조건 충족 시 자동 트리거되는 학습 파이프라인 구성

---

## **프로젝트 실행 방법**

streamlit을 통해 app.py를 구동할 수 있음
streamlit run app.py

```bash
# 1. 프로젝트 클론
git clone https://github.com/your-org/langchain-qa-project.git
cd langchain-qa-project

# 2. 가상환경 설정 및 패키지 설치
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 환경 변수 설정
export OPENAI_API_KEY=your-api-key

# 4. 실행
python main.py
```

---

## **활용 장비 및 사용 툴**

### **활용 장비**
- **서버:** AWS EC2 (m5.large), S3, ECR
- **개발 환경:** Ubuntu 22.04, Python 3.10+
- **테스트 환경:** NVIDIA V100 GPU 서버 (Lambda Labs 등)

### **협업 툴**
- **소스 관리:** GitHub
- **프로젝트 관리:** Jira, Confluence
- **커뮤니케이션:** Slack
- **버전 관리:** Git

### **사용 도구**
- **CI/CD:** GitHub Actions, Jenkins
- **LLM 통합:** LangChain, OpenAI API, HuggingFace
- **실험 관리:** MLflow, Optuna
- **데이터 관리:** DVC, AWS S3
- **모니터링:** Prometheus, Grafana, ELK Stack
- **배포 및 운영:** Docker, Kubernetes, Helm

---

## **기대 효과 및 향후 계획**
- 문서 기반 질문 응답 자동화로 고객 응대 시간 절감
- 사내 문서 검색 정확도 및 사용성 향상
- 향후 다양한 도메인 문서(QA, 정책, 교육자료 등)에 확장 적용 예정

---
## **강사님 피드백 및 프로젝트 회고**

프로젝트 진행 중 담당 강사님과의 피드백 세션을 통해 얻은 주요 인사이트는 다음과 같습니다.

### �� **1차 피드백 (YYYY.MM.DD)**
- 제한된 시간이 있으니, 데이터 카테고리를 늘리는 것보다 정부 혜택을 활용하여 품질을 높이는 것을 추천
- streamlit 혹은 gradio를 사용하여 결과물을 쉽게 내는 방법 추천
- 품질을 높이기 위해 다양한 기술 도입 필요 (ex.CAG GC)

### �� **2차 피드백 (YYYY.MM.DD)**
- 임베딩 비용 문제 때문에 데이터 업데이트 때 추가된 정책만 임베딩 하여 db에 저장할 경우, 유사도 관련 문제로 정확도가 떨어질 수 있음.

### �� **3차 피드백 (YYYY.MM.DD)**
- "기존 데이터로 임베딩한 후 새로운 데이터로 임베딩했을 때, faiss index로 추가해도 되나요? 혹은 새로운 임베딩을 학습해야하나요?"
A:  일단, faiss 라이브러리 같은 경우는 가능합니다.
그 이유는 faiss가 index탐색방법을 동적으로 추가할 수 있어서 자동으로 내부 그래프가 갱신이 됩니다. 단 조건이 있는데요. 같은 임베딩을 사용할 경우 가능하고, A임베딩으로 학습하고 B임베딩으로 학습한 새로운 데이터를 추가할 경우 그 표현력이 달라지기 떄문에 임베딩 재 빌드 형식으로 가야합니다. 일부 다른 라이브러리는 동적으로 추가하는 지원이 되지 않기 때문에 라이브러리 document를 잘 확인하시고 사용하시면 좋을 것 같고 임베딩을 추가하지 않고 임베딩을 재 빌드하는 형식으로 사용합니다.
동적으로 추가 안되는 알고리즘들은 Annoy, IVF 등등이 있을 것 같습니다! 