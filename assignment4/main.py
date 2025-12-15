import pandasql as spldf
import pandas as pd
import streamlit as st
import log_auth
import home 
import csv
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "Login" not in st.session_state:
    st.session_state.Login = False

def log():
    if st.session_state.Login:
        csv.csv()
        log_auth.log_in()
    else:
        log_auth.log_out()

with st.sidebar:
    if st.button("Home", use_container_width=True):
        st.session_state.page = "Home"
        
    if st.button("Login", use_container_width=True):
        st.session_state.page = "Login"
        st.session_state.Login = True
        

    if st.button("Register", use_container_width=True):
        st.session_state.page = "Register"

    
    # if st.button("Logout", use_container_width=True):
    #     st.session_state.Login = False
        
if st.session_state.page == "Home":
    st.set_page_config(page_title="Home Page")
    st.title("Home Page")
    home.home()

elif st.session_state.page == "Login":
    st.set_page_config(page_title="Login")
    st.title("Login Csv authentication")
    log_auth.log_in()
 

elif st.session_state.page == "Register":
    st.set_page_config(page_title="Register")
    st.title("Register Page")
