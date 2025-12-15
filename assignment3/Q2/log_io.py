import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Login page")
                   
api_key = os.getenv("API_KEY")
def log_in():
    st.title("Login Weather App")
    if "Logout_message" in st.session_state:
        st.success(st.session_state["Logout_message"])
        del st.session_state["Logout_message"]

    username = st.text_input("Enter Username")
    password = st.text_input("Enter password", type="password")
    if st.button("login", type = "primary"):
        if (username == "Anish" and password == "1234"):
            st.success("Login successful")
            st.session_state["Login"] = True
            st.rerun() 
        else:
            st.write("Incorrect username or password ")

def log_out():
    logout = st.button("Logout", type = "primary")
    if logout:
        st.session_state["Logout_message"] = "Thanks, You have been logged out Sucessfully"
        st.session_state["Login"] = False
        st.rerun() 