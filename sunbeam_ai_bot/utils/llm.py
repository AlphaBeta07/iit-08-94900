import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()
llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_llm(context, question):
    prompt = f"""
Answer the question using the given Sunbeam Institute data.

Context:
{context}

Question:
{question}
"""
    return llm.invoke(prompt).content
