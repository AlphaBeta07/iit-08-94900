from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

URL_MAP = {
    "home": "https://www.sunbeaminfo.in/",
    "about_us": "https://www.sunbeaminfo.in/about-us",
    "placements": "https://www.sunbeaminfo.in/placements",
    "workshops": "https://www.sunbeaminfo.in/workshops",
    "courses": "https://www.sunbeaminfo.in/courses",
    "admission": "https://www.sunbeaminfo.in/admission",
    "testimonials": "https://www.sunbeaminfo.in/testimonials",
    "infrastructure": "https://www.sunbeaminfo.in/infrastructure",
    "contact_us": "https://www.sunbeaminfo.in/contact-us"
}

def scrape():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(URL_MAP["home"])
    driver.implicitly_wait(5)
    text = driver.find_element(By.TAG_NAME, "body").text
    driver.quit()
    return text
