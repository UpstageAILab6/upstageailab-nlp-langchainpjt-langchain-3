# PDF 기반 질의응답 시스템

이 프로젝트는 RAG(Retrieval-Augmented Generation) 아키텍처를 활용하여 PDF 문서에 대한 질의응답 기능을 제공합니다.

## 기능

- PDF 문서 로드 및 처리
- 텍스트 분할 및 임베딩
- 벡터 데이터베이스 생성 및 검색
- 자연어 질의에 대한 컨텍스트 기반 응답
- 대화형 CLI(Command Line Interface)
- 벡터 인덱스 저장 및 로드 기능

## 구조

프로젝트는 모듈화된 구조로 설계되었습니다:

- `main.py`: 프로그램의 진입점
- `rag_pipeline.py`: RAG 파이프라인 클래스 정의
- `cli.py`: 커맨드 라인 인터페이스 관련 기능
- `utils.py`: 유틸리티 함수
- `config.py`: 설정 및 환경 변수 관리

## 설치

1. 필수 패키지 설치:

```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
   - `.env.example` 파일을 `.env`로 복사하고 필요한 API 키와 설정을 입력하세요.

```bash
cp .env.example .env
# .env 파일 편집
```

## 사용 방법

### 새 PDF 파일로 시작하기

```bash
python main.py --pdf 문서경로.pdf
```

예시:
```bash
python main.py --pdf data/SPRI_AI_Brief_2023년12월호_F.pdf
```

### 벡터 인덱스 저장하기

```bash
python main.py --pdf 문서경로.pdf --save-index
```

### 저장된 벡터 인덱스 로드하기

```bash
python main.py --load-index faiss_index/문서이름
```

### 추가 옵션

```bash
python main.py --help
```

## 대화형 인터페이스 사용법

프로그램 실행 후:
1. PDF 파일에 관련된 질문을 입력하세요.
2. 시스템이 문서에서 관련 정보를 검색하고 답변을 생성합니다.
3. 대화를 종료하려면 'exit'를 입력하세요.

## 프로젝트 확장

- 여러 PDF 파일 동시 처리 기능 추가
- 웹 인터페이스 구현
- 다국어 지원 강화
- 답변 품질 평가 메트릭 추가