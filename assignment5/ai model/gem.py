import os
import requests
import json
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

headers = {"Content-Type" : "application/json"}

st.title("AskAnish", text_alignment="center")
user_msg = st.chat_input("enter message : ")

if user_msg:
    data = {"contents" : [{"parts" : [{"text" : user_msg}]}]}

    response = requests.post(url, headers = headers, data = json.dumps(data))
    if response.status_code == 200:
        reply = response.json()
        bot_reply = reply["candidates"][0]["content"]["parts"][0]["text"]
        st.write(user_msg)
        st.write("→")
        st.write(bot_reply)
    else:
        st.error(f"API Error: {response.status_code}")
        st.json(response.json())



