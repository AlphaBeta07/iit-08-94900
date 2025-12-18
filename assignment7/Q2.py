import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

st.set_page_config(page_title="Weather App")
st.title("Weather App Bot")

API_KEY = os.getenv("API_KEY")
LM_STUDIO_URL = "http://localhost:1234/v1"

city = st.text_input("Enter City name:")


def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    r = requests.get(url, params=params, timeout=8)
    r.raise_for_status()
    d = r.json()

    return {
        "temp": d["main"]["temp"],
        "feels_like": d["main"]["feels_like"],
        "humidity": d["main"]["humidity"],
        "wind": d["wind"]["speed"],
        "description": d["weather"][0]["description"]
    }


def run_llm_stream(weather):
    llm = ChatOpenAI(
        model="google/gemma-3-4b",
        base_url=LM_STUDIO_URL,
        api_key="lm-studio",
        streaming=True,
        temperature=0.6
    )

    messages = [
        {
            "role": "system",
            "content": "You are a professional weather reporter."
        },
        {
            "role": "user",
            "content": f"""
            City: {city}
            Temperature: {weather['temp']} °C
            Feels Like: {weather['feels_like']} °C
            Humidity: {weather['humidity']} %
            Wind Speed: {weather['wind']} m/s
            Condition: {weather['description']}

            Explain the current weather clearly. 
            """
        }
    ]

    for chunk in llm.stream(messages):
        if chunk.content:
            yield chunk.content


if city:
    weather = get_weather(city)

    st.subheader("Current Weather")
    st.write(f"City : {city}")
    st.write(f"Temperature : {weather['temp']} °C")
    st.write(f"Feels Like : {weather['feels_like']} °C")
    st.write(f"Humidity : {weather['humidity']} %")
    st.write(f"Wind Speed : {weather['wind']} m/s")
    st.write(f"Condition : {weather['description']}")

    st.subheader("AI Weather Explanation")
    st.write_stream(run_llm_stream(weather))
