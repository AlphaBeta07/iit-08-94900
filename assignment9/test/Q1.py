import streamlit as st
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
import csv_page as cp
import scraper_page as sp
load_dotenv()

def add_chat(role, message):
    st.session_state.chat.append(
        {"role": role, "message": message}
    )
    
llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

st.title("Bot")

if "chat" not in st.session_state:
    st.session_state.chat = []

agent = st.sidebar.radio(
    "Choose Agent",
    ["CSV Agent", "Web Scraping Agent"]
)


for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["message"])

if agent == "CSV Agent":
    cp.csv(llm, add_chat)
    
if agent == "Web Scraping Agent":
    sp.scrap(llm, add_chat)