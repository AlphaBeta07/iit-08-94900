from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os

load_dotenv()

OPENAI_BASE_URL = "http://127.0.0.1:1234/v1/chat/completions"

llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url = os.environ.get("OPENAI_BASE_URL"),
    api_key = os.environ.get("OPENAI_API_KEY")
)

agent = create_agent(model=llm, tools=list())
result = agent.invoke(
    {"messages": [{"role": "user", "content" : "what is langchain"}]
    }
)
print(result["message"][-1].content)
