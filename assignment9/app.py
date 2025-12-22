import streamlit as st
from langchain.chat_models import init_chat_model
import os
import pandas as pd
import pandasql as ps
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import time

load_dotenv()

llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

st.title("Bot")

if "chat" not in st.session_state:
    st.session_state.chat = []

agent = st.sidebar.radio(
    "Choose Agent",
    ["CSV Agent", "Web Scraping Agent"]
)

def add_chat(role, message):
    st.session_state.chat.append(
        {"role": role, "message": message}
    )

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["message"])

if agent == "CSV Agent":

    csv_file = st.file_uploader("Select the CSV file", type=["csv"])

    if csv_file is not None:
        df = pd.read_csv(csv_file)
        st.dataframe(df)

        schema = ", ".join(
            [f"{c} ({t})" for c, t in zip(df.columns, df.dtypes)]
        )

        add_chat(
            "assistant",
            f"The CSV file has {len(df.columns)} columns: {', '.join(df.columns)}"
        )

        user_input = st.chat_input("Enter the message")

        if user_input:
            add_chat("user", user_input)

            llm_input = f"""
                Table Name: data
                Table Schema: {schema}
                Question: {user_input}

                Instruction:
                - Write only the SQL query
                - No explanation
                - If not possible, return error
                """

            query = llm.invoke(llm_input)
            sql_query = query.content.strip()

            st.write(sql_query)

            if sql_query.lower() == "error":
                st.error("Could not generate SQL query")
                add_chat("assistant", "I could not generate a valid SQL query.")
            else:
                try:
                    result_table = ps.sqldf(sql_query, {"data": df})
                    st.dataframe(result_table)

                    explanation = (
                        "I converted your question into an SQL query. "
                        "Then I executed the query on the uploaded CSV file. "
                        "The table shown above is the result."
                    )

                    add_chat("assistant", explanation)

                except Exception as e:
                    st.error("SQL execution failed")
                    add_chat("assistant", str(e))

if agent == "Web Scraping Agent":
    st.header("Web Scraping Agent")

    user_input = st.chat_input("Ask about Sunbeam internships")

    if user_input:
        add_chat("user", user_input)

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)

        driver.get("https://www.sunbeaminfo.in/internship")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        rows = driver.find_elements(By.TAG_NAME, "tr")

        keywords = user_input.lower().split()
        results = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            row_text = " ".join(c.text.lower() for c in cols)

            if any(k in row_text for k in keywords):
                results.append([c.text for c in cols])

        driver.quit()

        if results:
            st.subheader("Matching Internship Details")
            for r in results:
                st.write(" | ".join(r))
                st.divider()
            add_chat("assistant", "Here are the matching internship details from Sunbeam.")
        else:
            st.warning("No matching data found")
            add_chat("assistant", "No internship information matched your question.")
