import Q2
import weather
import streamlit as st

if "Login" not in st.session_state:
    st.session_state["Login"] = False

if st.session_state["Login"]:
    weather.weather()
    Q2.log_out()
else:
    Q2.log_in()