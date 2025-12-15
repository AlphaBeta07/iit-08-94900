import streamlit as st
def log_in():
    if "Logout_message" in st.session_state:
        st.success(st.session_state["Logout_message"])
        del st.session_state["Logout_message"]

    username = st.text_input("Enter Username")
    password = st.text_input("Enter password", type = "password")

    if st.button("Login"):
        if (username == "Anish" and password == "1234"):
            st.success("Logged In")
            st.session_state["Login"] = True
            st.rerun

        else: 
            st.write("Incorrect username or password")

def log_out():
    logout = st.button("Logout")
    if logout:
        st.session_state["Logout_message"] = "You have been logged out Successfully"
        st.session_state["Login"] = True
        st.rerun

