import mysql.connector
import streamlit as st
from langchain.chat_models import init_chat_model
import pandas as pd

host = "localhost"
user = "root"
password = "manager"
database = "test_db"
tables_name = "sample_table"

st.set_page_config(page_title="MySQL Bot", layout="wide")
st.title("MySQL Assistant")

llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

if "chat" not in st.session_state:
    st.session_state.chat = []

def add_chat(role, message, df=None):
    st.session_state.chat.append({"role": role, "message": message, "df": df})

# --- Database Connection ---
@st.cache_resource
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=host, user=user, password=password, 
            database=database, autocommit=True
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Connection failed: {err}")
        return None

conn = get_db_connection()

if conn:
    cursor = conn.cursor()
    # Get Schema
    cursor.execute(f"DESCRIBE {tables_name}")
    rows = cursor.fetchall()
    schema = ", ".join([f"{col} ({dtype})" for col, dtype, *_ in rows])
    
    with st.expander("Database Schema Details"):
        st.info(f"Connected to table: **{tables_name}**")
        st.text(f"Schema: {schema}")

    # Display Chat History
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.write(msg["message"])
            if msg.get("df") is not None:
                st.dataframe(msg["df"])

    # User Input
    user_input = st.chat_input("Ask a question about your data...")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        
        # 1. Generate SQL
        sql_prompt = f"""
        Table Name: {tables_name}
        Table Schema: {schema}
        Question: {user_input}
        Rules:
        - Return ONLY a valid MySQL query.
        - No explanation, no markdown.
        - Only SELECT, SHOW, or DESCRIBE.
        """
        
        sql_response = llm.invoke(sql_prompt).content.strip()
        sql_query = sql_response.replace("```sql", "").replace("```", "").strip()

        # 2. Execute SQL
        try:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(result, columns=columns)
                
                # 3. Generate Human Explanation
                explain_prompt = f"User question: {user_input}\nResult data: {result}\nTask: Explain this result in one simple sentence without mentioning SQL."
                explanation = llm.invoke(explain_prompt).content
                
                # Show in UI
                with st.chat_message("assistant"):
                    st.code(sql_query, language="sql")
                    st.dataframe(df)
                    st.write(explanation)
                
                # Save to history
                add_chat("user", user_input)
                add_chat("assistant", explanation, df=df)
            
        except mysql.connector.Error as e:
            st.error(f"SQL Error: {e}")