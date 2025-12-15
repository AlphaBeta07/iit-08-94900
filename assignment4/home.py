import streamlit as st
import log_auth as log


def home():
    #st.write("For unauthenticated users, the application should display a simple sidebar menu containing Home, Login, and Register options. User credentials entered during registration and login must be securely stored and validated using a users.csv file. Once a user successfully authenticates, the sidebar menu should dynamically change to show Explore CSV, See History, and Logout options. Authenticated users should be allowed to upload CSV files, and each upload action must be recorded in a userfiles.csv file, storing details such as user ID, CSV file name, and date-time of upload. The pandas library should be used for efficiently reading from and writing to both users.csv and userfiles.csv, ensuring proper data handling, persistence, and easy retrieval of user and upload history information.")
    if st.button("Try Now"):
        log.log_in()
home()