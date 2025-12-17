import json
import requests

url = "hhtp://localhost:1234/v1/chat/completions"

headers = {
    "Content-Type": "applications/json",
    "Authorizaztion": "Bearer not-needed"
}

data = {
    "model" : "microsoft/phi-4-mini-reasoning",
    "message" : [
        {"role": "user", "content": "Explain what quantization is in simple terms."}
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())