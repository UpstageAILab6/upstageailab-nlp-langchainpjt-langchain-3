"""
main.py - PDF 기반 질의응답 시스템의 주 진입점

이 스크립트는 RAG(Retrieval-Augmented Generation) 시스템을 사용하여
PDF 문서에 대한 질의응답 기능을 제공합니다.

사용법:
  python main.py --pdf 문서경로.pdf
  python main.py --load-index 저장된_인덱스경로

예시:
  python main.py --pdf data/SPRI_AI_Brief_2023년12월호_F.pdf
  python main.py --load-index faiss_index/SPRI_AI_Brief_2023년12월호_F
"""

import sys
import traceback

from cli import parse_arguments, setup_rag_pipeline, interactive_session
import utils


def main():
    """
    프로그램 메인 함수
    """
    try:
        # 명령줄 인수 파싱
        args = parse_arguments()
        
        # RAG 파이프라인 설정
        pipeline, pdf_filename = setup_rag_pipeline(args)
        
        # 대화형 세션 시작
        interactive_session(pipeline, pdf_filename)
        
    except FileNotFoundError as e:
        print(f"파일 오류: {str(e)}")
        return 1
    except ValueError as e:
        print(f"입력 오류: {str(e)}")
        return 1
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
        return 0
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())