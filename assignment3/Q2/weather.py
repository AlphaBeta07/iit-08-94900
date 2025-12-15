import requests
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Weather app")

api_key = os.getenv("API_KEY")
def weather():
    st.title("Weather App")
    city = st.text_input("Enter City name : ")

    if city:

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city,"appid": api_key,"units": "metric"}

        try:
            response = requests.get(url, params=params, timeout=8)
            weather = response.json()
            st.write("Temperature: ", weather["main"]["temp"]," °C")
            st.write("Humidity: ", weather["main"]["humidity"])
            st.write("Feels like: ", weather["main"]["feels_like"]," °C")
            st.write("Wind Speed: ", weather["wind"]["speed"]," m/s")
        except:
            st.write("City not found. Check spelling.")
weather()