import os
import re
import requests
import streamlit as st
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

load_dotenv()

# -------------------- LLM --------------------
llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# -------------------- EMBEDDINGS --------------------
embeddings = init_embeddings(
    model="text-embedding-nomic-embed-text-v1.5",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

# -------------------- SCRAPER (NO BEAUTIFULSOUP) --------------------
def scrape_sunbeam():
    url = "https://www.sunbeaminfo.in"
    response = requests.get(url, timeout=15)
    html = response.text

    text = re.sub("<script.*?>.*?</script>", "", html, flags=re.S)
    text = re.sub("<style.*?>.*?</style>", "", text, flags=re.S)
    text = re.sub("<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# -------------------- CREATE DOCUMENTS --------------------
def create_documents(raw_text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_text(raw_text)

    docs = []
    for i, chunk in enumerate(chunks):
        docs.append(
            Document(
                page_content=chunk,
                metadata={
                    "source": "sunbeaminfo.in",
                    "chunk_id": i
                }
            )
        )
    return docs

# -------------------- VECTOR STORE --------------------
def build_vector_db(docs):
    return Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="chroma_db"
    )

def load_vector_db():
    return Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="Sunbeam RAG Bot", layout="wide")
st.title("Sunbeam Institute RAG Assistant")

if st.button("Scrape & Index Sunbeam Website"):
    with st.spinner("Scraping website..."):
        raw_text = scrape_sunbeam()
        docs = create_documents(raw_text)
        vectordb = build_vector_db(docs)
        vectordb.persist()
    st.success("Website indexed successfully")

user_query = st.chat_input("Ask a question about Sunbeam Institute")

if user_query:
    vectordb = load_vector_db()

    with st.spinner("Searching relevant content..."):
        results = vectordb.similarity_search(user_query, k=4)

    context = "\n\n".join([doc.page_content for doc in results])

    prompt = f"""
You are an assistant answering questions using ONLY the context below.

Context:
{context}

Question:
{user_query}

Answer clearly and accurately.
"""

    with st.spinner("Generating answer..."):
        response = llm.invoke(prompt)

    st.subheader("Answer")
    st.write(response.content)

    st.subheader("Retrieved Chunks")
    for i, doc in enumerate(results):
        st.markdown(f"**Chunk {i+1}**")
        st.write(doc.page_content)
