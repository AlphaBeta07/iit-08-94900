"""
Design a Streamlit-based application with a sidebar to switch between Groq and LM Studio. 
The app should accept a user question and display responses using Groq’s cloud LLM and a locally running LM Studio model.
Also maintain and display the complete chat history of user questions and model responses.
"""
import os
import requests
import json
import time
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

url_groq = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

st.title("AskAnish", text_alignment= "center")

if "message" not in st.session_state:
    st.session_state.message = []

for msg in st.session_state.message:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

with st.sidebar:
    if st.button("Qroq", use_container_width=True):
        st.session_state.page = "Qroq"
    if st.button("LM Studio", use_container_width=True):
        st.session_state.page = "LM Studio"

user_msg = st.chat_input("Enter message:")

if user_msg:
    with st.chat_message("user"):
        st.write(user_msg)
    
    st.session_state.message.append({"role": "user", "content": user_msg})

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": user_msg}
        ]
    }
    try:
        response = requests.post(url_groq, headers=headers, data=json.dumps(data), timeout=10)
        
        if response.status_code == 200:
            reply = response.json()
            bot_reply = reply["choices"][0]["message"]["content"]
            with st.chat_message("assistant"):
                st.write_stream(stream_text(bot_reply))
            
            st.session_state.message.append({"role": "assistant", "content": bot_reply})
            
        else:
            st.error(f"API Error: {response.status_code}")
            st.json(response.json())

    except Exception as e:
        st.error(f"An error occurred: {e}")