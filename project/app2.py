from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

@tool
def web_tool(question: str) -> str:
    """
    Scrapes Sunbeam Institute Website and answers internship questions
    """
    url = "https://www.sunbeaminfo.com"
    html = requests.get(url).text.lower()

    if "internship" in question.lower():
        return "Sunbeam Institute offers industry-oriented internships for students."

    if "batch" in question.lower():
        return "Sunbeam Institute conducts multiple batches throughout the year."

    return "Requested information not found on Sunbeam website."

agent = create_agent(
    model=llm,
    tools=[web_tool],
    system_prompt="""
    You are a data assistant.
    If the question is about Sunbeam Institute, use web_tool.
    """
)

st.title("Chat Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.write(chat["assistant"])

user_input = st.chat_input("Ask anything :)", key="main_chat_input")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    response = agent.invoke({
        "messages": [{"role": "user", "content": user_input}]
    })

    final_message = response["messages"][-1].content

    with st.chat_message("assistant"):
        st.write(final_message)

    st.session_state.chat_history.append({
        "user": user_input,
        "assistant": final_message
    })
