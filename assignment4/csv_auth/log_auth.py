import streamlit as st
def log_in():
    if "Logout_message" in st.session_state:
        st.success(st.session_state["Logout_message"])
        del st.session_state["Logout_message"]

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "Anish" and password == "1234":
            return True
        else:
            st.error("Invalid username or password")
    return False

def log_out():
    logout = st.button("Logout")
    if logout:
        st.session_state["Logout_message"] = "You have been logged out Successfully"
        st.session_state["Login"] = True
        st.rerun()

