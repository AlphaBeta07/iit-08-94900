import requests
import json

url = "https://jsonplaceholder.typicode.com/posts"

try:
    data = requests.get(url).json()
    with open("posts.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Saved to posts.json")
except:
    print("Some error occured.")