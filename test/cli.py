"""
cli.py - 커맨드 라인 인터페이스 기능

이 모듈은 RAG 시스템의 커맨드 라인 인터페이스를 제공합니다.
사용자 입력 처리 및 대화형 세션 관리 기능이 포함됩니다.
"""

import argparse
import os
from pathlib import Path

import utils
from rag_pipeline import RAGPipeline
import config


def parse_arguments():
    """
    명령줄 인수를 파싱합니다.
    
    Returns:
        argparse.Namespace: 파싱된 인수
    """
    parser = argparse.ArgumentParser(
        description="PDF 문서 기반 질의응답 시스템",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--pdf", 
        type=str,
        help="질의응답에 사용할 PDF 문서의 경로"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default=config.DEFAULT_MODEL,
        help="사용할 LLM 모델 이름"
    )
    
    parser.add_argument(
        "--temperature", 
        type=float, 
        default=config.DEFAULT_TEMPERATURE,
        help="모델의 temperature 매개변수 (0~1)"
    )
    
    parser.add_argument(
        "--chunk-size", 
        type=int, 
        default=config.DEFAULT_CHUNK_SIZE,
        help="문서 분할에 사용할 청크 크기"
    )
    
    parser.add_argument(
        "--save-index", 
        action="store_true",
        help="생성된 벡터 인덱스를 저장할지 여부"
    )
    
    parser.add_argument(
        "--load-index",
        type=str,
        help="기존 벡터 인덱스를 로드할 경로"
    )
    
    parser.add_argument(
        "--enable-langsmith",
        action="store_true",
        help="LangSmith 모니터링 활성화"
    )
    
    return parser.parse_args()


def interactive_session(rag_pipeline, pdf_filename):
    """
    대화형 질의응답 세션을 시작합니다.
    
    Args:
        rag_pipeline (RAGPipeline): 초기화된 RAG 파이프라인
        pdf_filename (str): 사용 중인 PDF 파일 이름
    """
    utils.clear_screen()
    utils.print_banner("PDF 기반 질의응답 시스템")
    
    print(f"\n{pdf_filename}에서 어떤 정보를 찾아드릴까요?\n")
    print("(대화를 종료하려면 'exit'를 입력하세요)\n")
    
    while True:
        # 사용자 입력 받기
        question = input("\n질문: ")
        
        # 종료 조건 검사
        if question.lower() == 'exit':
            print("\n대화를 종료합니다. 감사합니다!")
            break
        
        # 빈 입력 처리
        if not question.strip():
            print("질문을 입력해주세요.")
            continue
        
        try:
            # 사용자 질문에 대한 답변 생성
            print("\n답변 생성 중...", end="\r")
            answer = rag_pipeline.query(question)
            
            # 타이핑 효과로 답변 출력
            print(" " * 20, end="\r")  # 진행 메시지 지우기
            utils.print_with_typing_effect(f"\n답변: {answer}")
            
        except Exception as e:
            print(f"\n오류 발생: {str(e)}")


def setup_rag_pipeline(args):
    """
    RAG 파이프라인을 설정합니다.
    
    Args:
        args (argparse.Namespace): 명령줄 인수
        
    Returns:
        tuple: (RAGPipeline, str) - 초기화된 파이프라인과 PDF 파일 이름
    """
    # PDF 파일 검증 및 로드
    if args.load_index:
        # 저장된 인덱스 로드
        if not os.path.exists(args.load_index):
            raise FileNotFoundError(f"벡터 인덱스를 찾을 수 없습니다: {args.load_index}")
        
        # 인덱스만 로드하는 경우 더미 PDF 경로 사용
        pdf_path = args.pdf or "dummy_path.pdf"
        pdf_filename = utils.get_filename(pdf_path)
        
        print(f"저장된 인덱스 로드 중: {args.load_index}")
        pipeline = RAGPipeline.load_vectorstore(
            path=args.load_index,
            model_name=args.model,
            temperature=args.temperature,
            enable_langsmith=args.enable_langsmith
        )
        
    else:
        # PDF 파일 검증
        if not args.pdf:
            raise ValueError("PDF 파일 경로를 지정해주세요 (--pdf 옵션).")
        
        pdf_path = utils.validate_pdf_path(args.pdf)
        pdf_filename = utils.get_filename(pdf_path)
        
        # 새 파이프라인 초기화 및 실행
        print(f"파이프라인 초기화 중: {pdf_filename}")
        pipeline = RAGPipeline(
            pdf_path=pdf_path,
            chunk_size=args.chunk_size,
            model_name=args.model,
            temperature=args.temperature,
            enable_langsmith=args.enable_langsmith
        )
        
        print("PDF 처리 중...")
        pipeline.run_pipeline()
        
        # 인덱스 저장 (요청된 경우)
        if args.save_index:
            index_dir = config.DEFAULT_VECTOR_STORE_PATH
            utils.create_directory_if_not_exists(index_dir)
            index_path = os.path.join(index_dir, Path(pdf_filename).stem)
            pipeline.save_vectorstore(index_path)
            print(f"벡터 인덱스 저장됨: {index_path}")
    
    return pipeline, pdf_filename