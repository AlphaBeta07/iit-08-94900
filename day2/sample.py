import streamlit as st
import pandas as pd
st.title("ChatBot")

with st.slider:
    st.header("Settings")
    options = ["Upper", "Lower", "Toggle"]
    case = st.selectbox("Select case", options)
    


name = st.text_input("enter name)")
message  = st.text_area("enter your name: ", height = 100)
file  = st.file_uploader("choose a file ", type = ['csv', 'pdf'])
model = st.selectbox("Choose Ai model : ", ["GPt4", "Gemini"])
if name:
    st.write(f"hello, {name}")

st.markdown("**this is bold ** and ** this is itlaic **")

df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
st.dataframe(df)

config  = {"model": "gpt4", "temp ": 0.7}
st.json(config)