import requests
import streamlit as st
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

st.set_page_config(page_title="Weather App")

api_key = os.getenv("API_KEY")
llm_url = "http://localhost:1234/v1/chat/completions"
st.title("Weather App Bot")

city = st.text_input("Enter City name:")

def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    response = requests.get(url, params=params, timeout=8)
    response.raise_for_status()
    data = response.json()

    weather_info = {
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "feels_like": data["main"]["feels_like"],
        "wind": data["wind"]["speed"],
        "description": data["weather"][0]["description"]
    }

    return weather_info


def run_llm(weather_info):
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemma-3-4b",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional weather reporter."
            },
            {
                "role": "user",
                "content": f"""
                City: {city}
                Temperature: {weather_info['temp']} °C
                Feels Like: {weather_info['feels_like']} °C
                Humidity: {weather_info['humidity']} %
                Wind Speed: {weather_info['wind']} m/s
                Condition: {weather_info['description']}

                Explain the current weather clearly.
                """
            }
        ]
    }

    response = requests.post(
        llm_url,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


if city:
    weather_info = get_weather(city)

    st.subheader("Current Weather")
    st.write(F"City : {city}")
    st.write(f"Temperature : {weather_info['temp']} °C")
    st.write(f"Feels Like : {weather_info['feels_like']} °C")
    st.write(f"Humidity : {weather_info['humidity']} %")
    st.write(f"Wind Speed : {weather_info['wind']} m/s")
    st.write(f"Condition : {weather_info['description']}")

    # if st.button("Explain Weather"):
    #     explanation = run_llm(weather_info)
    #     st.subheader("AI Weather Explanation")
    #     st.write(explanation)
    explanation = run_llm.stream(weather_info)
    st.subheader("AI Weather Explanation")
    st.write(explanation)
