import streamlit as st
from langchain.chat_models import init_chat_model
import os
import pandas as pd
import pandasql as ps
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider="openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)

conversation = [
    {"role":"system", "content": "Yous are SQLite expert developer with 10 years of experience." }
]

csv_file = st.file_uploader("Select the csv file")
if csv_file is not None:
    df = pd.read_csv(csv_file)

    st.dataframe(df)

    user_input = st.chat_input("Enter the message")
    if user_input:
        llm_input = f"""
            Table Name : data
            Table Schema : {df}
            Question : {user_input}
            Instruction:
                write a SQL query for the above question only,
                generate SQL query only in plain text format,
                give only query and nothing else so that i can run it directly without any changes, 
                if you cannot generate the query print `error`
        """
        query = llm.invoke(llm_input)
        
        st.write(query.content)

        if query.content == "error":
            st.write("error")
        else:
            result_table = ps.sqldf(query.content, {"data": df})
            st.write(result_table)
