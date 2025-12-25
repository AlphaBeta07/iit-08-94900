import streamlit as st
import log_auth
import home
import csv_page
import reg

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "Login" not in st.session_state:
    st.session_state.Login = False

with st.sidebar:
    if st.button("Home", use_container_width=True):
        st.session_state.page = "Home"

    if not st.session_state.Login:
        if st.button("Login", use_container_width=True):
            st.session_state.page = "Login"

        if st.button("Register", use_container_width=True):
            st.session_state.page = "Register"
    else:
        if st.button("CSV", use_container_width=True):
            st.session_state.page = "CSV"

        if st.button("Logout", use_container_width=True):
            st.session_state.Login = False
            st.session_state.page = "Home"

# -------- Page Routing --------

if st.session_state.page == "Home":
    st.title("Home Page")
    home.homee()
elif st.session_state.page == "Register":
    st.title("Registration Page")
    reg.regis()

elif st.session_state.page == "Login":
    st.title("Login")
    if log_auth.log_in():
        st.session_state.Login = True
        st.session_state.page = "CSV"
        st.rerun()

elif st.session_state.page == "CSV":
    if st.session_state.Login:
        csv_page.csv()
    else:
        st.warning("Please login first")
