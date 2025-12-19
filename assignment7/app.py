import streamlit as st
from langchain.chat_models import init_chat_model
import pandas as pd
from pandasql import sqldf
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

csv_file = st.file_uploader("Upload a CSV file", type=["csv"])

if csv_file is not None:
    df = pd.read_csv(csv_file)
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(" ", "_")
    )

    st.subheader("Dataset Preview")
    st.dataframe(df)
    user_input = st.chat_input("Ask a question about the data", key="csv_chat")

    if user_input:
        sql_prompt = f"""
        You are an SQLite expert.
        Table name: data
        Table schema:{df.dtypes}
        Question:{user_input}
        Rules:
        - Generate ONLY a valid SQL query
        - No explanation
        - Use table name `data`
        - If not possible, output `error`
        """

        sql_response = llm.invoke(sql_prompt)
        sql_query = sql_response.content.strip()

        st.subheader("Generated SQL Query")
        st.code(sql_query, language="sql")

        if sql_query.lower() != "error":
            try:
                result_df = sqldf(sql_query, {"data": df})

                st.subheader("Query Result")
                st.dataframe(result_df)
                explain_prompt = f"""
                    Explain the following SQL result in simple English:
                    {result_df.head().to_string(index=False)}
                    """
                explanation = llm.invoke(explain_prompt)

                st.subheader("Explanation")
                st.write(explanation.content)

            except Exception as e:
                st.error("SQL Execution Error")
                st.code(str(e))
