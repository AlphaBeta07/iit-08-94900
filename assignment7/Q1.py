from langchain.chat_models import init_chat_model
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider="openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)

conversation = [
    {"role":"system", "conten": "Yous are SQLite expert developer with 10 years of experience." }
]

csv_file = input("Enter the file csv file")
df = pd.read_csv(csv_file)
print("CSV Schema : ")
print(df.dtypes)

while True:
    user_input = input("Enter the message")
    if user_input == "exit":
        break
    llm_input = f"""
        Table Name : data
        Table Schema : {df.dtypes}
        Question : {user_input}
        Instruction:
            write a SQL query for the above question
            generate SQL query only in plain text format and run the SQL command and display the dataframe
            it you cannot generate the query print `error`
    """
    result = llm.invoke(llm_input)
    print(result.content)