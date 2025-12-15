import log_io
import weather
import streamlit as st

if "Login" not in st.session_state:
    st.session_state["Login"] = False

if st.session_state["Login"]:
    weather.weather()
    log_io.log_out()
else:
    log_io.log_in()