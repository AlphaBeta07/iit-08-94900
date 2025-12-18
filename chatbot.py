import os
import time
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.set_page_config(page_title="AskAnish", layout="centered")
st.title("AskAnish")

gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

def stream_text(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

user_msg = st.chat_input("Enter message")

if user_msg:
    st.session_state.messages.append(
        {"role": "user", "content": user_msg}
    )

    with st.chat_message("user"):
        st.write(user_msg)

    response = gemini.invoke(st.session_state.messages)

    st.session_state.messages.append(
        {"role": "assistant", "content": response.content}
    )

    with st.chat_message("assistant"):
        st.write_stream(stream_text(f"{response.content}"))
