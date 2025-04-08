from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter

def split_by_char(documents, chunk_size=800, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)

def split_by_token(documents, chunk_size=1000, chunk_overlap=150):
    splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)