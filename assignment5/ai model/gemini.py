import os
import requests
import json
import time
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"

headers = {"Content-Type": "application/json"}

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

user_msg = st.chat_input("Enter message:")

if user_msg:
    with st.chat_message("user"):
        st.write(user_msg)
    
    st.session_state.message.append({"role": "user", "content": user_msg})

    data = {"contents": [{"parts": [{"text": user_msg}]}]}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        
        if response.status_code == 200:
            reply = response.json()
            bot_reply = reply["candidates"][0]["content"]["parts"][0]["text"]
            with st.chat_message("assistant"):
                st.write_stream(stream_text(bot_reply))
            
            st.session_state.message.append({"role": "assistant", "content": bot_reply})
            
        else:
            st.error(f"API Error: {response.status_code}")
            st.json(response.json())

    except Exception as e:
        st.error(f"An error occurred: {e}")