import requests
api_key="f5fbf3d88546b398a1e0e56b97b1b45b"
city = input("Enter city: ")
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
try:
    response = requests.get(url)
    print("status:", response.status_code)
    weather = response.json()
    print("Temperature: ", weather["main"]["temp"]," °C")
    print("Humidity: ", weather["main"]["humidity"])
    print("Feels like: ", weather["main"]["feels_like"]," °C")
    print("Wind Speed: ", weather["wind"]["speed"]," m/s")
except:
    print("City not found. Check spelling.")