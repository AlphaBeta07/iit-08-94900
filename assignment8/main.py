from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_react_agent  # Modern implementation
from langchain.tools import tool
import os
import requests

load_dotenv()

weather_API_KEY = os.getenv("API_KEY")

# 1. Setup LLM
llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

# 2. Define Tools with Docstrings (Fixes the ValueError)
@tool
def calculator(expression: str) -> str:
    """Useful for when you need to answer math questions. Input should be a valid python expression."""
    allowed = {"__builtins__": {}}
    return str(eval(expression, allowed))

@tool
def file_reader(path: str) -> str:
    """Use this to read the content of a local file. Provide the full file path as a string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@tool
def current_weather(city: str) -> str:
    """Fetch the current weather for a given city in Celsius."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": weather_API_KEY,
        "units": "metric"
    }
    r = requests.get(url, params=params, timeout=8)
    r.raise_for_status()
    d = r.json()
    return f"Temperature: {d['main']['temp']}°C, Weather: {d['weather'][0]['description']}"

@tool
def knowledge_lookup(topic: str) -> str:
    """Lookup general information or definitions about a specific topic."""
    return f"General information about {topic}: LangChain is a framework for building LLM applications."

tools = [calculator, file_reader, current_weather, knowledge_lookup]

# 3. Create the Agent
# Note: create_react_agent is the standard way to combine tools and LLM in recent LangChain
agent_executor = create_react_agent(llm, tools)

# 4. Implement Logging Middleware
# We can wrap the execution to observe the input/output flow
def run_agent_with_logging(user_input: str):
    print(f"\n--- LOGGING MIDDLEWARE: Processing '{user_input}' ---")
    
    # Executing the agent
    response = agent_executor.invoke({"messages": [("user", user_input)]})
    
    # Inspecting Message History
    print("--- MESSAGE HISTORY FLOW ---")
    for msg in response["messages"]:
        role = msg.__class__.__name__.replace("Message", "")
        content = msg.content if msg.content else f"[Tool Call: {msg.tool_calls}]"
        print(f"[{role}]: {content}")
    
    print("-" * 50)
    return response["messages"][-1].content

# 5. Testing
print(run_agent_with_logging("Calculate 12 * 5 + 8"))
print(run_agent_with_logging("What is the weather in Pune?"))
print(run_agent_with_logging("Explain LangChain using knowledge lookup"))