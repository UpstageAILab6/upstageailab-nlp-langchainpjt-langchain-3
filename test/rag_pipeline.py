import os
from dotenv import load_dotenv
import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class RAGPipeline:
    """
    PDF 문서 기반 질의응답을 위한 Retrieval-Augmented Generation (RAG) 파이프라인.
    
    이 클래스는 다음과 같은 RAG 워크플로우를 구현합니다:
    1. PDF에서 문서 로드
    2. 텍스트를 청크로 분할
    3. 임베딩 생성
    4. 벡터 데이터베이스 생성 및 저장
    5. 리트리버 설정
    6. 프롬프트 템플릿 설정
    7. LLM 구성
    8. 체인 생성 및 실행
    """
    
    def __init__(self, pdf_path=None, chunk_size=500, chunk_overlap=50, 
                model_name="gpt-4o-mini", temperature=0, 
                enable_langsmith=False, langsmith_project="RAG-Project"):
        """
        RAG 파이프라인을 구성 매개변수로 초기화합니다.
        
        Args:
            pdf_path (str): PDF 문서 경로
            chunk_size (int): 텍스트 분할 청크 크기
            chunk_overlap (int): 청크 간 겹침 정도
            model_name (str): LLM 모델 이름
            temperature (float): LLM 온도 매개변수
            enable_langsmith (bool): LangSmith 로깅 활성화 여부
            langsmith_project (str): LangSmith 프로젝트 이름
        """
        # 환경 변수 로드
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # 구성
        self.pdf_path = pdf_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model_name = model_name
        self.temperature = temperature
        
        # LangSmith 로깅 설정 (활성화된 경우)
        if enable_langsmith:
            self._setup_langsmith(langsmith_project)
        
        # 컴포넌트 초기화
        self.docs = None
        self.split_documents = None
        self.vectorstore = None
        self.retriever = None
        self.chain = None
        
        # 프롬프트 템플릿 초기화
        self.prompt = PromptTemplate.from_template(
            """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Answer in Korean. 

#Question: 
{question} 
#Context: 
{context} 

#Answer:"""
        )
    
    def _setup_langsmith(self, project_name):
        """
        추적 및 평가를 위한 LangSmith 로깅을 설정합니다.
        
        Args:
            project_name (str): LangSmith 프로젝트 이름
        """
        try:
            from langchain_teddynote import logging as langsmith_logging
            langsmith_logging.langsmith(project_name)
            print(f"LangSmith 추적을 시작합니다.\n[프로젝트명]\n{project_name}")
        except ImportError:
            logging.warning("LangSmith 로깅을 사용할 수 없습니다. pip install langchain-teddynote로 설치하세요.")
    
    def load_document(self, pdf_path=None):
        """
        PDF 문서를 로드합니다.
        
        Args:
            pdf_path (str, optional): PDF 문서 경로. 제공되지 않으면 초기화 시 경로를 사용합니다.
            
        Returns:
            self: 메서드 체이닝 지원
        """
        if pdf_path:
            self.pdf_path = pdf_path
        
        if not self.pdf_path:
            raise ValueError("PDF 경로가 제공되지 않았습니다")
        
        loader = PyMuPDFLoader(self.pdf_path)
        self.docs = loader.load()
        print(f"문서 페이지 수: {len(self.docs)}")
        return self
    
    def split_document(self):
        """
        문서를 청크로 분할합니다.
        
        Returns:
            self: 메서드 체이닝 지원
        """
        if not self.docs:
            raise ValueError("문서가 로드되지 않았습니다. load_document()를 먼저 호출하세요.")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap
        )
        self.split_documents = text_splitter.split_documents(self.docs)
        print(f"분할된 청크 수: {len(self.split_documents)}")
        return self
    
    def create_vectorstore(self):
        """
        임베딩 및 벡터 스토어를 생성합니다.
        
        Returns:
            self: 메서드 체이닝 지원
        """
        if not self.split_documents:
            raise ValueError("문서가 분할되지 않았습니다. split_document()를 먼저 호출하세요.")
        
        embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.from_documents(
            documents=self.split_documents, 
            embedding=embeddings
        )
        return self
    
    def setup_retriever(self):
        """
        문서 검색을 위한 리트리버를 설정합니다.
        
        Returns:
            self: 메서드 체이닝 지원
        """
        if not self.vectorstore:
            raise ValueError("벡터 스토어가 생성되지 않았습니다. create_vectorstore()를 먼저 호출하세요.")
        
        self.retriever = self.vectorstore.as_retriever()
        return self
    
    def create_chain(self):
        """
        질의응답을 위한 LLM 체인을 생성합니다.
        
        Returns:
            self: 메서드 체이닝 지원
        """
        if not self.retriever:
            raise ValueError("리트리버가 설정되지 않았습니다. setup_retriever()를 먼저 호출하세요.")
        
        llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | llm
            | StrOutputParser()
        )
        return self
    
    def run_pipeline(self):
        """
        로딩부터 체인 생성까지 완전한 RAG 파이프라인을 실행합니다.
        
        Returns:
            self: 메서드 체이닝 지원
        """
        return (self
                .load_document()
                .split_document()
                .create_vectorstore()
                .setup_retriever()
                .create_chain())
    
    def query(self, question):
        """
        RAG 파이프라인에 질의를 실행합니다.
        
        Args:
            question (str): 답변할 질문
            
        Returns:
            str: LLM의 답변
        """
        if not self.chain:
            raise ValueError("체인이 생성되지 않았습니다. create_chain() 또는 run_pipeline()을 먼저 호출하세요.")
        
        return self.chain.invoke(question)
    
    def save_vectorstore(self, path="faiss_index"):
        """
        벡터 스토어를 디스크에 저장합니다.
        
        Args:
            path (str): 벡터 스토어를 저장할 경로
            
        Returns:
            self: 메서드 체이닝 지원
        """
        if not self.vectorstore:
            raise ValueError("벡터 스토어가 생성되지 않았습니다. create_vectorstore()를 먼저 호출하세요.")
        
        self.vectorstore.save_local(path)
        print(f"벡터 스토어가 {path}에 저장되었습니다")
        return self
    
    @classmethod
    def load_vectorstore(cls, path="faiss_index", **kwargs):
        """
        기존 벡터 스토어로 파이프라인을 로드합니다.
        
        Args:
            path (str): 저장된 벡터 스토어 경로
            **kwargs: RAGPipeline 생성자에 대한 추가 인수
            
        Returns:
            RAGPipeline: 로드된 벡터 스토어가 있는 새 파이프라인 인스턴스
        """
        pipeline = cls(**kwargs)
        embeddings = OpenAIEmbeddings()
        pipeline.vectorstore = FAISS.load_local(path, embeddings)
        pipeline.setup_retriever().create_chain()
        return pipeline