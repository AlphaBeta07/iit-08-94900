import streamlit as st
import os
import pandas as pd

def regis():
    st.header("Register")

    with st.form("reg_form"):
        username = st.text_input("Enter Name")
        password = st.text_input("Enter Password", type="password")
        submit = st.form_submit_button("Submit", type="primary")

    if submit:
        if not username or not password:
            st.warning("All fields are required")
            return

        file = "user.csv"

        if os.path.exists(file) and os.path.getsize(file) > 0:
            df = pd.read_csv(file)
        else:
            df = pd.DataFrame(columns=["username", "password"])

        if username in df["username"].values:
            st.error("User already exists")
        else:
            df.loc[len(df)] = [username, password]
            df.to_csv(file, index=False)
            st.success("Registration successful, please login")
