import streamlit as st
import os
import time
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import init_chat_model

import chromadb
from chromadb.config import Settings

load_dotenv()

URL = "https://www.sunbeaminfo.in/"

st.set_page_config(page_title="Sunbeam AI Web Bot", layout="wide")
st.title("Sunbeam Institute – AI Web Scraping Bot")

# -------------------- Selenium Scraper --------------------
def scrape_website(url: str) -> str:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(url)
    time.sleep(5)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    driver.quit()

    return body_text


# -------------------- Chunking --------------------
def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    return splitter.split_text(text)


# -------------------- Vector DB --------------------
def setup_vector_db(chunks):
    client = chromadb.Client(
        Settings(persist_directory="./sunbeam_db", anonymized_telemetry=False)
    )

    collection = client.get_or_create_collection(name="sunbeam")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    for i, chunk in enumerate(chunks):
        vector = embeddings.embed_query(chunk)
        collection.add(
            documents=[chunk],
            embeddings=[vector],
            metadatas=[{"source": URL, "chunk_id": i}],
            ids=[f"chunk_{i}"]
        )

    return collection, embeddings


# -------------------- LLM --------------------
llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)


# -------------------- UI --------------------
if st.button("Scrape & Index Sunbeam Website"):
    with st.spinner("Scraping website using Selenium..."):
        text = scrape_website(URL)

    with st.spinner("Chunking text..."):
        chunks = chunk_text(text)

    with st.spinner("Creating embeddings & storing in ChromaDB..."):
        collection, embedding_model = setup_vector_db(chunks)

    st.success("Website indexed successfully")

# -------------------- Query --------------------
query = st.text_input("Ask a question about Sunbeam Institute")

if query:
    client = chromadb.Client(
        Settings(persist_directory="./sunbeam_db", anonymized_telemetry=False)
    )
    collection = client.get_collection(name="sunbeam")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    query_embedding = embedding_model.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=4
    )

    context = "\n\n".join(results["documents"][0])

    prompt = f"""
You are an AI assistant for Sunbeam Institute.

User Question:
{query}

Relevant Website Content:
{context}

Answer clearly and accurately based ONLY on the above content.
"""

    with st.spinner("Generating answer..."):
        response = llm.invoke(prompt)

    st.subheader("Answer")
    st.write(response.content)

    with st.expander("Retrieved Chunks"):
        for doc in results["documents"][0]:
            st.write(doc)
            st.write("---")
