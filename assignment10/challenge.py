import mysql.connector
import streamlit as st
from langchain.chat_models import init_chat_model
import pandas as pd

host = "localhost"
user = "root"
password = "manager"
database = "test_db"
tables_name = "sample_table"


st.title("MySQL Bot")

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["message"])

def add_chat(role, message):
    st.session_state.chat.append(
        {"role": role, "message": message}
    )

llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

try:
    connection = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database,
        autocommit = True
    )
    st.write("Connected to mysql")

    cursor = connection.cursor()
    
except mysql.connector.Error as err:
    st.error(err)


cursor.execute(f"DESCRIBE {tables_name}")
rows = cursor.fetchall()

schema = ", ".join(
    [f"{col} ({dtype})" for col, dtype, *_ in rows]
)

st.write("Table schema:", schema)

# add_chat(
#     "assistant",
#     "I have generated the SQL query based on your question. "
# )

user_input = st.chat_input("Enter the message")

if user_input:
    
    add_chat("user", user_input)

    llm_prompt = f"""
    Table Name: {tables_name}
    Table Schema: {schema}

    Question: {user_input}

    Rules:
    - Return ONLY a valid MySQL query
    - No explanation
    - No markdown
    - Only SELECT, SHOW, or DESCRIBE
    - If not possible return ERROR
    """

    llm_response = llm.invoke(llm_prompt)
    sql_query = llm_response.content.strip()

    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    st.code(sql_query, language="sql")

    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()

        if cursor.description and result:
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(result, columns=columns)
            st.dataframe(df)
        else:
            st.warning("Query executed successfully, but no rows were returned.")

        prompt = f"""
        user question: {user_input}
        generated query: {sql_query}
        result: {result}

        task:
        Explain the result in simple English.
        Do not mention SQL or databases.
        Assume the user has no technical background.
        """

        explanation = llm.invoke(prompt)
        st.subheader("Explanation")
        add_chat("assistant", explanation.content)



    except mysql.connector.Error as e:
        st.error(f"SQL Execution Error: {e}")
        add_chat("assistant", str(e))
    # if sql_query.lower() == "error":
    #     st.error("Could not generate SQL")
    #     add_chat("assistant", "I could not generate a valid SQL query.")

    # elif not sql_query.lower().startswith(("select", "show", "describe")):
    #     st.error("Unsafe SQL detected")
    #     add_chat("assistant", "Unsafe SQL was blocked.")

    # else:
    #     try:
    #         cursor.execute(sql_query)
    #         result = cursor.fetchall()

    #         if cursor.description:
    #             columns = [desc[0] for desc in cursor.description]
    #             df = pd.DataFrame(result, columns=columns)
    #             st.dataframe(df)
    #         else:
    #             st.success("Query executed successfully")

    #         add_chat(
    #             "assistant",
    #             "Your question was converted into SQL and executed on MySQL."
    #         )

    #     except mysql.connector.Error as e:
    #         st.error(f"SQL Execution Error: {e}")
    #         add_chat("assistant", str(e))