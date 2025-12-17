import os
import requests
import time
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
GOOGLE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GOOGLE_API_KEY}"


GROQ_HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}
GOOGLE_HEADERS = {"Content-Type": "application/json"}

st.set_page_config(page_title="AskAnish", layout="centered")
st.title("AskAnish")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    model_choice = st.radio("Choose Model",["Groq ", "LM Studio", "Gemini"])
    
def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.04)

def ask_groq(prompt):
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(GROQ_URL,headers=GROQ_HEADERS,json=data,timeout=15)
    return response.json()["choices"][0]["message"]["content"]

def ask_lm_studio(prompt):
    data = {
        "model": "local-model",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 512
    }
    response = requests.post(LM_STUDIO_URL,json=data,timeout=60)
    return response.json()["choices"][0]["message"]["content"]

def ask_gemini(prompt):
    data = {"contents": [{"parts": [{"text": user_msg}]}]}
    response = requests.post(GOOGLE_URL, headers=GOOGLE_HEADERS, json = data, timeout=10)
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.caption(msg["model"])
        st.write(msg["content"])

user_msg = st.chat_input("Enter your question...")

if user_msg:
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.write(user_msg)

    with st.spinner("Thinking"):
        try:
            if model_choice == "Groq":
                bot_reply = ask_groq(user_msg)
            elif model_choice == "LM Studio":
                bot_reply = ask_lm_studio(user_msg)
            else:
                bot_reply = ask_gemini(user_msg)

            
        except Exception as e:
            bot_reply = f"Error: {e}"

    with st.chat_message("assistant"):
        st.caption(model_choice)
        st.write_stream(stream_text(bot_reply))

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply,"model": model_choice})
