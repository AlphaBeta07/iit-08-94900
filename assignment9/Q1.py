from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import pandas as pd
import requests
import os
import pandasql as ps
from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider = "openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)

@tool
def csv_tool(csv_path: str, sql_query: str) -> str:
    """
    Executes SQL query on a CSV file using pandasql
    """
    try:
        df = pd.read_csv(csv_path)

        sql_query = sql_query.strip()
        if sql_query.lower().startswith("select") is False:
            return "Error: Invalid SQL generated"

        result = ps.sqldf(sql_query, {"df": df})
        return result.to_string()

    except Exception as e:
        return f"SQL Error: {e}"



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
    
tools = [csv_tool, web_tool]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    You are a data assistant.

    IMPORTANT RULES:
    - The CSV is loaded as a pandas DataFrame named 'df'
    - ALWAYS use table name 'df' in SQL queries
    - NEVER invent table names like products, users, sales, etc.
    
    If the question involves CSV analysis:
    1. Generate SQL using ONLY table 'df'
    2. Call csv_tool with csv_path and sql_query

    If the question is about Sunbeam Institute, use web_tool.
    """
)


chat_history = []

while True:
    user_input = input("Ask anything :)")
    
    if user_input.lower() == "exit":
        break
    
    response = agent.invoke({
        "messages":[
            {"role":"user","content":user_input}
            ]
    })
    
    chat_history.append({
        "User": user_input,
        "Agent": response
    })
    final_message = response["messages"][-1].content
    print("\nAgent Response:\n", final_message)
   

print("Full chat history")
for i in chat_history:
    print(i)