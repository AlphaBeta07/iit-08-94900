import streamlit as st
import pandas as pd
from pandasql import sqldf

def csv():
    st.title("CSV SQL")
    file = st.file_uploader("choose the file", type = "csv")
    if file:
        df = pd.read_csv(file)
        st.dataframe(df)

        query = st.text_area("enter the sql query (table name - df)")

        if st.button("exectue"):
            result = sqldf(query, {"df": df})
            st.dataframe(result)
