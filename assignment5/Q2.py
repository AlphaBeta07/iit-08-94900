import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
    f"?key={GEMINI_API_KEY}"
)

GROQ_HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

GEMINI_HEADERS = {
    "Content-Type": "application/json"
}

user_input = input("Enter message: ")

groq_data = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "user", "content": user_input}
    ]
}

gemini_data = {
    "contents": [
        {
            "parts": [
                {"text": user_input}
            ]
        }
    ]
}

start_time = time.time()
groq_response = requests.post(
    GROQ_URL,
    headers=GROQ_HEADERS,
    data=json.dumps(groq_data)
)
groq_time = time.time() - start_time

start_time = time.time()
gemini_response = requests.post(
    GEMINI_URL,
    headers=GEMINI_HEADERS,
    data=json.dumps(gemini_data)
)
gemini_time = time.time() - start_time

groq_result = groq_response.json()
gemini_result = gemini_response.json()

print("Groq Response:")
print(groq_result["choices"][0]["message"]["content"])
print("Time Taken:", round(groq_time, 3), "seconds")

print("\nGemini Response:")
print(gemini_result["candidates"][0]["content"]["parts"][0]["text"])
print("Time Taken:", round(gemini_time, 3), "seconds")

print("\nSpeed Comparison:")
if groq_time < gemini_time:
    print("Groq is faster")
else:
    print("Gemini is faster")
