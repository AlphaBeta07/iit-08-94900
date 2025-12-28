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

llm = init_chat_model( #using cloud based api
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)

if "conversation" not in st.session_state:#every time the user types something, 
                                          #it gets stored and displayed, maintaining the chat history.
                                          #st.session_state checks if conversation is in list if not then it adds the conversation
    st.session_state.conversation = []

#streamlit ui  
st.title("Resume Manager")

menu = st.sidebar.selectbox(
    "Menu",
    ["Upload Resume","List Resumes","Delete Resumes","Shortlist Resumes"]
)

#initialize embedding model
embedding_model = init_embeddings(
    model="text-embedding-nomic-embed-text-v1.5",
    provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed",
    check_embedding_ctx_length=False
)

#Create Chroma DB Client (Persistent) This is Resume Knowledge Base
CHROMA_DIR = "chroma_db"

client = chromadb.Client(
    Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    )
)

#Create / Load Resume Collection
collection = client.get_or_create_collection(
    name="resumes"
)

st.sidebar.write("Stored resume chunks:", collection.count())

#Function: Store Resume into Chroma DB
def store_resume_in_chromadb(resume_text, resume_name):
    # 1. Split resume into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(resume_text)

    # 2. Create embeddings for chunks
    embeddings = embedding_model.embed_documents(chunks)

    # 3. Create unique IDs for each chunk
    ids = [f"{resume_name}_{i}" for i in range(len(chunks))]

    # 4. Metadata for each chunk
    metadatas = [{"resume_name": resume_name} for _ in chunks]

    # 5. Store in Chroma DB
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
#file uploading via streamlit
if menu == "Upload Resume":
    data_file = st.file_uploader("Upload a PDF file",type=["pdf"], accept_multiple_files=True) #list of files are stored in data_file
    
    Resume_dir = "resumes" #Defines a folder name where resumes will be saved.
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
            file_path = os.path.join(Resume_dir, file.name) #- Builds a path (file_path) inside the resumes folder using the file’s original name.
        
        #duplicate file restriction
        if os.path.exists(file_path):
            st.warning(f"{file.name} already uploaded.")
              
        #save pdf file
        with open(file_path,"wb") as f :
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
        
        for i,name in enumerate(resume_names,start=1):
            st.write(f"{i}.{name}")

elif menu == "Delete Resumes":
    st.subheader("Delete Resume")
    
    data = collection.get(include=["metadatas"])
    
    if not data["metadata"]:
        st.info("No resumes available to delete")
    else:
        resume_names = sorted(
            set(meta["resume_name"] for meta in data["metadatas"])
        )
        
        selected_resume = st.select_box(
            "select a resume to delete",
            resume_names
        )
        
        if st.button("Delete Resume"):
            #1 delete from chroma db
            collection.delete(
                where={"resume_name" : selected_resume}
            )
            
            # 2. Delete PDF file from disk
            file_path = os.path.join("resumes", selected_resume)
            if os.path.exists(file_path):
                os.remove(file_path)

            st.success(f"{selected_resume} deleted successfully.")
            st.experimental_rerun()

        
#Function: Retrieve relevant resume chunks 
def retrieve_resume_chunks(question, top_k=5): #retrieves resume contents
    # 1. Convert question into embedding
    question_embedding = embedding_model.embed_query(question)

    # 2. Query Chroma DB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    # 3. Extract retrieved documents
    retrieved_chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    return retrieved_chunks, metadatas
# STEP 4: Answer question using retrieved resume chunks
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


    
#chat input loop
user = st.chat_input("Say something") #creates chat style input box
if user:
    st.session_state.conversation.append( #Conversation state management
        {"role": "user", "content": user} 
    )

    #context = st.session_state.conversation  #adds users message to conversation history & llm invocation
    response_text = answer_question_from_resumes(user)
           


    st.session_state.conversation.append( # Passes the entire conversation history to your 
                                          # language model (llm) so it can generate a context-aware reply.
                                          # Appending assistant response
        {"role": "assistant", "content": response_text}
    )
    
for msg in st.session_state.conversation:  #- Stores the assistant’s reply in the conversation list.
    with st.chat_message(msg["role"]):     #- Displaying messages
        st.markdown(msg["content"])        #- Iterates through the conversation and renders each message
                                           # in a chat bubble, styled by role (user vs assistant).


    


