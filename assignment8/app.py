from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
import os
import requests

load_dotenv()

WEATHER_API_KEY = os.getenv("API_KEY")

llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    allowed = {"__builtins__": {}}
    return str(eval(expression, allowed))


@tool
def file_reader(path: str) -> str:
    """Read a text file and return its content."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@tool
def current_weather(city: str) -> str:
    """Get current weather details for a city."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }
    r = requests.get(url, params=params, timeout=8)
    r.raise_for_status()
    d = r.json()
    return (
        f"Temperature: {d['main']['temp']}°C, "
        f"Feels like: {d['main']['feels_like']}°C, "
        f"Humidity: {d['main']['humidity']}%, "
        f"Weather: {d['weather'][0]['description']}"
    )

@tool
def knowledge_lookup(topic: str) -> str:
    """Provide general information about a topic."""
    return f"General information about {topic}"

tools = [
    calculator,
    file_reader,
    current_weather,
    knowledge_lookup
]

agent = create_agent(
    model=llm,
    tools=tools
)

def log_messages(messages):
    print("----- MESSAGE HISTORY -----")
    for m in messages:
        print(m)
    print("---------------------------")

response1 = agent.invoke({
    "messages": [
        {"role": "user", "content": "Calculate 15 * 4 + 20"}
    ]
})
log_messages(response1["messages"])
print("Final Answer:", response1["messages"][-1].content)

response2 = agent.invoke({
    "messages": [
        {"role": "user", "content": "What is the current weather in Pune?"}
    ]
})
log_messages(response2["messages"])
print("Final Answer:", response2["messages"][-1].content)

response3 = agent.invoke({
    "messages": [
        {"role": "user", "content": "Explain LangChain"}
    ]
})
log_messages(response3["messages"])
print("Final Answer:", response3["messages"][-1].content)
