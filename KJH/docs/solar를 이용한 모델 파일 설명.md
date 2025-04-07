# 📁 KJH 프로젝트 파일 설명

## `.env`
- API 키 및 환경 변수 설정 파일입니다. Git에 업로드되지 않아야 합니다.

## `EDA.ipynb`
- 탐색적 데이터 분석(EDA)을 수행하는 노트북입니다.

## `langchain+solar.ipynb`
- LangChain과 Solar API를 테스트하는 노트북입니다.

## `main.py`
- RAG 전체 파이프라인을 실행하는 메인 스크립트입니다.

## `data/combined_service_data_merged.json`
- 병합된 서비스 데이터입니다. 최신 데이터 기준으로 사용됩니다.

## `data/combined_service_data_merged_prev.json`
- 이전 버전의 병합 서비스 데이터입니다. 변경 비교용입니다.

## `data/combined_service_data_prev.json`
- 병합 전 원본 서비스 데이터의 이전 버전입니다.

## `data/serviceDetail_all.json`
- 각 서비스에 대한 상세 정보를 포함한 JSON 파일입니다.

## `data/serviceDetail_all_prev.json`
- 이전 버전의 서비스 상세 정보입니다.

## `data/supportConditions_all.json`
- 서비스 지원 조건 데이터를 포함한 JSON입니다.

## `data/supportConditions_all_prev.json`
- 이전 버전의 지원 조건 데이터입니다.

## `data/supportConditions_model.json`
- 크롤링 또는 모델링된 지원 조건 데이터입니다.

## `data/supportConditions_model_prev.json`
- 이전 버전의 모델링된 지원 조건 데이터입니다.

## `data_pipeline/gov24_api_fetcher.py`
- 보조금24 공공API에서 데이터를 불러오는 모듈입니다.

## `data_pipeline/gov24_data_pipeline.py`
- 공공 데이터 수집부터 전처리까지 전체 파이프라인을 정의합니다.

## `data_pipeline/support_model_crawler.py`
- Selenium을 이용하여 지원 조건 모델 데이터를 수집합니다.

## `docs/data_pipeline_module_docs.md`
- 데이터 파이프라인 모듈 설명 문서입니다.

## `docs/env_settings.md`
- .env 파일 구성 설명 문서입니다.

## `docs/solar를 이용한 모델 파일 설명.md`
- Solar 기반 임베딩 및 LLM 활용 설명입니다.

## `docs/임베딩_전처리_및_선택_기록.md`
- 데이터 전처리 및 임베딩 선택 기준 기록입니다.

## `faiss_index/index.faiss`
- FAISS 벡터 인덱스 데이터입니다.

## `faiss_index/index.pkl`
- FAISS 인덱스에 대한 메타 정보입니다.

## `modules/chunk_splitter.py`
- 청크 분할 관련 로직을 포함하는 모듈입니다.

## `modules/data_loader.py`
- JSON 파일 로드 및 변경 감지, Document 변환을 포함한 데이터 처리 모듈입니다.

## `modules/llm_prompt.py`
- LLM용 프롬프트 생성 및 Solar API 호출을 담당하는 모듈입니다.

## `modules/query_and_search.py`
- 유사 문서 검색을 위한 쿼리 처리 모듈입니다.

## `modules/upstage_embedding.py`
- Upstage Solar Embedding API를 사용한 벡터화 모듈입니다.
