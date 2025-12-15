import streamlit as st
import time 

st.set_page_config(page_title="ChatBot UI")
st.title("ChatBot UI")

with st.sidebar:
    st.header("Setting")

if "message" not in st.session_state:
    st.session_state.message = []

for msg in st.session_state.message:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

def response(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.1)

chat_ip = st.chat_input("Enter Message")

if chat_ip:
    st.session_state.message.append({"role": "user", "content": chat_ip})
    with st.chat_message("user"):
        st.write(chat_ip)

    bot_reply = f"You said : {chat_ip}"

    st.session_state.message.append({"role": "user", "content": chat_ip})
    with st.chat_message("assistant"):
        st.write_stream(response(bot_reply))