from langchain_text_splitters import RecursiveCharacterTextSplitter #Used to break long resume text into small chunks
from langchain_community.document_loaders import PyPDFLoader #Used to read PDF files and extract text from them
from chromadb.config import Settings #Used to configure ChromaDB settings, like:where data is stored 
from langchain.chat_models import init_chat_model #Used to initialize the LLM
from langchain.embeddings import init_embeddings #Used to create embeddings (numeric vectors) from text
import streamlit as st
from dotenv import  load_dotenv
import pandas as pd
import chromadb #vectordatabase where resumes are stored
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import re

load_dotenv()
llm = ChatGoogleGenerativeAI( #using cloud based api
    model="gemini-1.5-flash",
    model_provider="google-genai",
    # base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GOOGLE_API_KEY}",
    api_key = os.getenv("GOOGLE_API_KEY")
)

if "conversation" not in st.session_state:
    st.session_state.conversation = []

st.title("Resume Manager")

menu = st.sidebar.selectbox("Menu",["Upload Resume","List Resumes","Delete Resumes","Shortlist Resumes"],index=0)

embedding_model = init_embeddings(
    model="text-embedding-nomic-embed-text-v1.5-embedding",
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


def clean_jd_text(jd):
    jd = jd.lower()
    jd = re.sub(r"give me|list me|such resume|please", "", jd)
    return jd.strip()
   
def shortlist_resumes(job_description, top_k_chunks=20):
    jd_embedding = embedding_model.embed_query(job_description)
    
    results = collection.query( #computing distance by cosine similrity .query does it internally
        query_embeddings=[jd_embedding],
        n_results=top_k_chunks,
        include=["metadatas"]
    )
    
    if not results["metadatas"]:
        return[]
    
    resume_score = {}
    
    for meta in results["metadatas"][0]:
        resume_name = meta["resume_name"]
        resume_score[resume_name] = resume_score.get(resume_name, 0)+1
        
    shortlisted = []
    
    for resume in resume_score:
        shortlisted.append((resume, resume_score[resume]))
        
    shortlisted.sort(reverse=True)
    return shortlisted
     
def retrieve_resume_chunks(question, top_k=5): #retrieves resume contents
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

    
#file uploading via streamlit
if menu == "Upload Resume":
    data_file = st.file_uploader("Upload a PDF/DOCX file",type=["pdf", "docx"], accept_multiple_files=True) #list of files are stored in data_file
    
    Resume_dir = "resumes" #defines a folder name where resumes will be saved.
    os.makedirs(Resume_dir, exist_ok=True) #Creates the folder if it doesn’t already exist.
    #if single pdf comes
    def load_pdf_resume(file_path):
        loader = PyPDFLoader(file_path) #- PyPDFLoader(data_file): Uses LangChain’s PyPDFLoader to read the PDF file
        docs = loader.load() #- docs = loader.load(): Loads the document into a list of Document objects, each representing a page.
       
         #concatenation loop - Collects all page text into one big string.
        resume_content = "\n\n".join([page.page_content for page in docs])
        metadata = {                     #returns meta data dictionary - Stores the file path and number of pages.
            "source" : file_path,        #- Return values: Returns (resume_content, metadata)
            "page_count" : len(docs)
        }
    
        return resume_content,metadata
    if data_file:
        for file in data_file:
            file_path = os.path.join(Resume_dir, file.name) 
        
        #duplicate file restriction
            if os.path.exists(file_path):
                st.warning(f"{file.name} already uploaded.")
              
        #save pdf file
            with open(file_path,"wb") as f : #"wb" stands for write binary, used to store non-text files like PDFs without corruption
                f.write(file.getbuffer())
            
            resume_text, metadata = load_pdf_resume(file_path)
            store_resume_in_chromadb(resume_text, file.name)
            st.success(f"{file.name} uploaded successfully")

elif menu == "List Resumes":
    st.subheader("Uploaded Resumes")
    
    data = collection.get(include=["metadatas"])
    
    if not data["metadatas"]:
        st.info("No resumes uploaded yet")
    else:
        resume_names = sorted(
            set(meta["resume_name"] for meta in data["metadatas"])
        )
        
        for i,name in enumerate(resume_names,start=1):
            st.write(f"{i}.{name}")

elif menu == "Delete Resumes":
    st.subheader("Delete Resume")

    data = collection.get(include=["metadatas"])

    if not data["metadatas"]:
        st.info("No resumes available to delete")
    else:
        resume_names = sorted(set(meta["resume_name"] for meta in data["metadatas"]))

        for resume in resume_names:
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(resume)

            with col2:
                if st.button("Delete", key=f"delete_{resume}"):
                    collection.delete(where={"resume_name": resume})

                    file_path = os.path.join("resumes", resume)
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    st.success(f"{resume} deleted successfully")
                    st.rerun()

elif menu == "Shortlist Resumes":
    st.subheader("Resume Shortlisting")
    job_description = st.text_area("Enter job description here",height=200)      
    top_n = st.number_input("Number of resumes to shortlist",min_value=1,max_value=10,value=3)
    
    if st.button("Shortlist"):
        if not job_description.strip():
            st.warning("Please enter a job description")
        else:
            clean_jd = clean_jd_text(job_description)
            shortlisted = shortlist_resumes(clean_jd)
            
            if not shortlisted:
                st.info("No matching resumes found")
            else:
                st.success("Shortlisted Resumes")
                
                for i, (resume, score) in enumerate(shortlisted[:top_n], start=1):
                    st.write(f"**{i}. {resume}** - Match score: {score}")


if menu in ["Shortlist Resumes"]:
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