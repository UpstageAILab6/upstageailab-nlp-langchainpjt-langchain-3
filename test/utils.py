import os
import sys
import time
from pathlib import Path


def validate_pdf_path(pdf_path):
    """
    PDF 파일 경로를 검증합니다.
    
    Args:
        pdf_path (str): 검증할 PDF 파일 경로
        
    Returns:
        str: 유효한 PDF 파일의 절대 경로
        
    Raises:
        FileNotFoundError: 파일이 존재하지 않는 경우
        ValueError: 파일이 PDF가 아닌 경우
    """
    path = Path(pdf_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")
    
    if path.suffix.lower() != '.pdf':
        raise ValueError(f"제공된 파일은 PDF가 아닙니다: {path}")
    
    return str(path)


def get_filename(file_path):
    """
    파일 경로에서 파일 이름만 추출합니다.
    
    Args:
        file_path (str): 파일 경로
        
    Returns:
        str: 파일 이름 (확장자 포함)
    """
    return os.path.basename(file_path)


def print_with_typing_effect(text, delay=0.01):
    """
    타이핑 효과로 텍스트를 출력합니다.
    
    Args:
        text (str): 출력할 텍스트
        delay (float): 문자 간 지연 시간(초)
    """
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def create_directory_if_not_exists(directory_path):
    """
    디렉토리가 존재하지 않는 경우 생성합니다.
    
    Args:
        directory_path (str): 생성할 디렉토리 경로
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"디렉토리 생성됨: {directory_path}")


def clear_screen():
    """
    터미널 화면을 지웁니다. 플랫폼에 따라 적절한 명령 사용.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner(title, width=60):
    """
    텍스트 배너를 출력합니다.
    
    Args:
        title (str): 배너에 표시할 제목
        width (int): 배너 너비
    """
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)