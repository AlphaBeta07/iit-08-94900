from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

file_path = input("Enter PDF file path: ")

loader = PyPDFLoader(file_path)
docs = loader.load()

for page in docs:
    print(page.page_content)
    print(page.metadata)

text_splitter_1 = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks_1 = text_splitter_1.split_documents(docs)

for chunk in chunks_1:
    print(chunk.page_content)

text_splitter_2 = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
)

chunks_2 = text_splitter_2.split_documents(docs)

for chunk in chunks_2:
    print(chunk.page_content)

text_splitter_3 = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

chunks_3 = text_splitter_3.split_documents(docs)

for chunk in chunks_3:
    print(chunk.page_content)
