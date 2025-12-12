import requests
import json

url = "https://nilesh-g.github.io/learn-web/data/novels.json"

try:
    data = requests.get(url).json()
    with open("posts.json", "w") as f:
        json.dump(data, f, indent=4)
    print("Saved to posts.json")
except:
    print("Some error occured.")