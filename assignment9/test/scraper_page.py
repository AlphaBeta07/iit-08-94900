import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# def add_chat(role, message):
#     st.session_state.chat.append(
#         {"role": role, "message": message}
#     )

def scrap(llm, add_chat):
    st.header("Web Scraping Agent")

    user_input = st.chat_input("Ask about Sunbeam internships")

    if user_input:
        add_chat("user", user_input)

        keyword_prompt = f"""
        Extract important search keywords from the following question.
        Return only comma-separated keywords. No explanation.

        Question:{user_input}
        """

        keyword_response = llm.invoke(keyword_prompt)
        keywords = [k.strip().lower() for k in keyword_response.content.split(",")]

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)

        driver.get("https://www.sunbeaminfo.in/internship")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        rows = driver.find_elements(By.TAG_NAME, "tr")

        results = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            row_text = " ".join([c.text.lower() for c in cols])

            if any(k in row_text for k in keywords):
                results.append([c.text for c in cols])

        driver.quit()

        if results:
            st.subheader("Matching Internship Details")
            for r in results:
                st.write(" | ".join(r))
                st.divider()

            add_chat(
                "assistant",
                f"I analyzed your question, extracted keywords ({', '.join(keywords)}), and found matching internship data from Sunbeam."
            )
        else:
            st.warning("No matching data found")
            add_chat(
                "assistant",
                "I understood your question, but the requested information was not found on the internship page."
            )

