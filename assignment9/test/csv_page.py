import streamlit as st
import pandas as pd
from pandasql import sqldf

def csv(llm, add_chat):
    csv_file = st.file_uploader("Select the CSV file", type=["csv"])

    if csv_file is not None:
        df = pd.read_csv(csv_file)
        st.dataframe(df)

        schema = ", ".join(
            [f"{c} ({t})" for c, t in zip(df.columns, df.dtypes)]
        )

        add_chat(
            "assistant",
            f"The CSV file has {len(df.columns)} columns: {', '.join(df.columns)}"
        )

        user_input = st.chat_input("Enter the message")

        if user_input:
            add_chat("user", user_input)

            llm_input = f"""
            Table Name: data
            Table Schema: {schema}
            Question: {user_input}

            Instruction:
            - Write only the SQL query
            - No explanation
            - If not possible, return error
            """

            query = llm.invoke(llm_input)
            sql_query = query.content.strip()

            st.write(sql_query)

            if sql_query.lower() == "error":
                st.error("Could not generate SQL query")
                add_chat("assistant", "I could not generate a valid SQL query.")
            else:
                try:
                    result_table = sqldf(sql_query, {"data": df})
                    st.dataframe(result_table)

                    add_chat(
                        "assistant",
                        "I converted your question into an SQL query and executed it on the CSV."
                    )

                except Exception as e:
                    st.error("SQL execution failed")
                    add_chat("assistant", str(e))
