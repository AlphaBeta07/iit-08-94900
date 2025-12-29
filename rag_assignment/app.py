import os
import tempfile
import streamlit as st
import chromadb

from dotenv import load_dotenv
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

st.set_page_config(page_title="Resume Manager", layout="wide")
st.title("Resume Manager")

if "history" not in st.session_state:
    st.session_state.history = []

client = chromadb.Client(
    Settings(
        persist_directory="./chroma_db",
        anonymized_telemetry=False
    )
)

collection = client.get_or_create_collection("resumes")

llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-nomic-embed-text-v1.5",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed",
    check_embedding_ctx_length=False
)

menu = st.sidebar.selectbox(
    "Menu",
    ["Upload Resume", "List Resumes", "Delete Resume", "Shortlist Resumes"]
)

def add_history(role, content):
    st.session_state.history.append({"role": role, "content": content})

if menu == "Upload Resume":
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

    if uploaded_file and st.button("Process Resume"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            file_path = tmp.name

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(documents)

        for i, doc in enumerate(chunks):
            vector = embeddings.embed_query(doc.page_content)
            collection.add(
                documents=[doc.page_content],
                embeddings=[vector],
                ids=[f"{uploaded_file.name}_{i}"]
            )

        st.success("Resume indexed successfully")

if menu == "List Resumes":
    results = collection.get()
    resume_names = set(id.split("_")[0] for id in results["ids"])

    if resume_names:
        for name in resume_names:
            st.write(name)
    else:
        st.info("No resumes found")

if menu == "Delete Resume":
    results = collection.get()
    resume_names = sorted(set(id.split("_")[0] for id in results["ids"]))

    resume_to_delete = st.selectbox("Select Resume", resume_names)

    if st.button("Delete"):
        ids_to_delete = [id for id in results["ids"] if id.startswith(resume_to_delete)]
        collection.delete(ids=ids_to_delete)
        st.success("Resume deleted")

if menu == "Shortlist Resumes":
    job_desc = st.text_area("Enter Job Description")

    if st.button("Shortlist"):
        query_vector = embeddings.embed_query(job_desc)
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=5
        )

        context = "\n\n".join(results["documents"][0])

        prompt = f"""
        You are an HR expert.
        Based on the job description below, shortlist the most relevant resumes.

        Job Description:
        {job_desc}

        Resumes:
        {context}
        """

        response = llm.invoke(prompt)
        st.write(response.content)
