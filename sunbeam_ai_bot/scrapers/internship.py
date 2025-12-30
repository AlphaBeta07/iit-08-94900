from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.sunbeaminfo.in/internship")
    driver.implicitly_wait(5)

    tbody = driver.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 7:
            continue
        data.append(
            f"Batch {cols[1].text}, Duration {cols[2].text}, Fees {cols[6].text}"
        )

    driver.quit()
    return "\n".join(data)
