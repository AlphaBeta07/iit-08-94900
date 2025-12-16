import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

headers = {"Content-Type" : "application/json"}

user_msg = input("enter message : ")

data = {"contents" : [{"parts" : [{"text" : user_msg}]}]}

response = requests.post(url, headers = headers, data = json.dumps(data))
#print(response.json())
print(json.dumps(response.json(), indent=4))
