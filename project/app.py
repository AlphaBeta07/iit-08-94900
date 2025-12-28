import streamlit as st
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
import chromadb
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GOOGLE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GOOGLE_API_KEY}"

GOOGLE_HEADERS = {"Content-Type": "application/json"}

llm = init_chat_model( #using cloud based api
    model="gemini-2.5-flash-lite",
    model_provider="google",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)

if "conversation" not in st.session_state:
    st.session_state.conversation = []


st.title("Resume Checker")

menu = st.sidebar.selectbox(
    "Menu",
    ["Upload Resume","List Resumes","Delete Resumes","Shortlist Resumes"]
)

embedding_model = init_embeddings(
    model="text-embedding-nomic-embed-text-v1.5-embedding",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed",
    check_embedding_ctx_length=False
)

CHROMA_DIR = "chroma_db"

client = chromadb.Client (
    Settings(
        persist_directory = CHROMA_DIR,
        anonaymized_telemerty = False
    )
)

coll

st.file_uploader("Upload the resume file", type=["pdf", "docx"])