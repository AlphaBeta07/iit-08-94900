from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from chromadb.config import Settings
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
import streamlit as st
import pandas as pd
import chromadb
import tempfile
import os

llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

if "conversation" not in st.session_state:
    st.session_state.conversation = []

st.title("Resume Manager")

menu = st.sidebar.selectbox(
    "Menu",
    ["Upload Resume", "List Resumes", "Delete Resumes", "Shortlist Resumes"]
)

embedding_model = init_embeddings(
    model="text-embedding-nomic-embed-text-v1.5",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed",
    check_embedding_ctx_length=False
)

CHROMA_DIR = "chroma_db"

client = chromadb.Client(
    Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    )
)

collection = client.get_or_create_collection(
    name="resumes"
)

st.sidebar.write("Stored resume chunks:", collection.count())

def store_resume_in_chromadb(resume_text, resume_name):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(resume_text)
    embeddings = embedding_model.embed_documents(chunks)
    ids = [f"{resume_name}_{i}" for i in range(len(chunks))]
    metadatas = [{"resume_name": resume_name} for _ in chunks]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

if menu == "Upload Resume":
    data_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        accept_multiple_files=True
    )

    Resume_dir = "resumes"
    os.makedirs(Resume_dir, exist_ok=True)

    def load_pdf_resume(file_path):
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        resume_content = "\n\n".join([page.page_content for page in docs])
        metadata = {
            "source": file_path,
            "page_count": len(docs)
        }
        return resume_content, metadata

    if data_file:
        for file in data_file:
            file_path = os.path.join(Resume_dir, file.name)

            if os.path.exists(file_path):
                st.warning(f"{file.name} already uploaded.")
                continue

            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            resume_text, metadata = load_pdf_resume(file_path)
            st.success(f"{file.name} uploaded successfully")
            store_resume_in_chromadb(resume_text, file.name)

elif menu == "List Resumes":
    st.subheader("Uploaded Resumes")

    data = collection.get(include=["metadatas"])

    if not data["metadatas"]:
        st.info("No resumes uploaded yet")
    else:
        resume_names = sorted(
            set(meta["resume_name"] for meta in data["metadatas"])
        )

        for i, name in enumerate(resume_names, start=1):
            st.write(f"{i}. {name}")

elif menu == "Delete Resumes":
    st.subheader("Delete Resume")

    data = collection.get(include=["metadatas"])

    if not data["metadatas"]:
        st.info("No resumes available to delete")
    else:
        resume_names = sorted(
            set(meta["resume_name"] for meta in data["metadatas"])
        )

        selected_resume = st.selectbox(
            "Select a resume to delete",
            resume_names
        )

        if st.button("Delete Resume"):
            collection.delete(
                where={"resume_name": selected_resume}
            )

            file_path = os.path.join("resumes", selected_resume)
            if os.path.exists(file_path):
                os.remove(file_path)

            st.success(f"{selected_resume} deleted successfully.")
            st.experimental_rerun()

def retrieve_resume_chunks(question, top_k=5):
    question_embedding = embedding_model.embed_query(question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    retrieved_chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    return retrieved_chunks, metadatas

def answer_question_from_resumes(question):
    chunks, metadatas = retrieve_resume_chunks(question)

    if not chunks:
        return "I could not find any relevant information in the uploaded resumes."

    context_text = "\n\n".join(chunks)

    prompt = f"""
        You are an AI assistant for HR.
        Answer the question using ONLY the resume information below.
        If the answer is not present, say "Information not found in resumes".

        Resume Information:
        {context_text}

        Question:
        {question}

        Answer:
        """

    response = llm.invoke(prompt)
    return response.content

user = st.chat_input("Say something")

if user:
    st.session_state.conversation.append(
        {"role": "user", "content": user}
    )

    response_text = answer_question_from_resumes(user)

    st.session_state.conversation.append(
        {"role": "assistant", "content": response_text}
    )

for msg in st.session_state.conversation:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
