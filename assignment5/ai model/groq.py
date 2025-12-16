import requests
import os

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
    "Content-Type": "application/json"
}

user_msg = input("Enter the message: ")

data = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "user", "content": user_msg}
    ]
}

response = requests.post(url, headers=headers, json=data)

print("Status:", response.status_code)
print(response.json()["choices"][0]["message"]["content"])
