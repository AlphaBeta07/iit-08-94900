from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

driver.get("https://www.sunbeaminfo.in/internship")
print("Page Title:", driver.title)
print("-" * 80)

driver.implicitly_wait(5)

tbody = driver.find_element(By.TAG_NAME, "tbody")
rows = tbody.find_elements(By.TAG_NAME, "tr")

for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")

    if len(cols) < 7:
        continue

    print(
        f"SR: {cols[0].text} | "
        f"Batch: {cols[1].text} | "
        f"Duration: {cols[2].text} | "
        f"Start: {cols[3].text} | "
        f"End: {cols[4].text} | "
        f"Time: {cols[5].text} | "
        f"Fees: {cols[6].text}"
    )

driver.quit()
