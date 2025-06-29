import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pdfminer.high_level import extract_text

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.breuninger.com/cz/service/terms-of-service/")

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)

try:
    cookie_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
    )
    cookie_button.click()
    time.sleep(10)
except:
    pass

driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})

result = driver.execute_cdp_cmd("Page.printToPDF", {
    "printBackground": True,
})

with open("output.pdf", "wb") as f:
    f.write(base64.b64decode(result['data']))

filename = "output.pdf"
text = extract_text(filename)

with open("output.txt", "w", encoding="utf-8") as f:
        f.write(text)

driver.quit()
