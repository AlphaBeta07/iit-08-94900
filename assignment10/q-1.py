import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

st.title("PDF Chunking using LangChain")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    file_path = f"/tmp/{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader(file_path)
    docs = loader.load()

    st.subheader("Original PDF Content")
    for page in docs:
        st.text(page.page_content)

    st.subheader("Chunking Example 1 (chunk_size=500, overlap=50)")
    splitter_1 = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks_1 = splitter_1.split_documents(docs)

    for i, chunk in enumerate(chunks_1, start=1):
        st.markdown(f"**Chunk {i}**")
        st.text(chunk.page_content)

    st.subheader("Chunking Example 2 (chunk_size=200, overlap=20)")
    splitter_2 = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )
    chunks_2 = splitter_2.split_documents(docs)

    for i, chunk in enumerate(chunks_2, start=1):
        st.markdown(f"**Chunk {i}**")
        st.text(chunk.page_content)

    st.subheader("Chunking Example 3 (chunk_size=1000, overlap=100)")
    splitter_3 = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks_3 = splitter_3.split_documents(docs)

    for i, chunk in enumerate(chunks_3, start=1):
        st.markdown(f"**Chunk {i}**")
        st.text(chunk.page_content)
