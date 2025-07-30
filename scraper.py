import os
import re
import sys
import time
import logging

from flask import Flask, jsonify
from urllib.parse import urljoin, unquote
from pdfminer.high_level import extract_text
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
# 🔧 Логгинг
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

# 📚 Ключевые слова для поиска ссылок на условия
TERMS_KEYWORDS = [
    "aktuální obchodní podmínky", "obchodní podmínky", "obchodni-podminky",
    "prodejní podmínky", "podmínky prodeje", "všeobecné obchodní podmínky",
    "terms and conditions", "terms", "vop", "general terms",
    "obchodni_podminky", "všeobecné prodejní podmínky", "vše o nákupu"
]

# 🧠 Очистка текста
def clean_text(text):
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

# 🚗 Headless Chrome driver
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")


    driver = webdriver.Chrome(options=options)    
    return driver
# 🔎 Поиск ссылки на условия
def find_terms_link(driver, homepage_url):
    try:
        driver.get(homepage_url)
        time.sleep(2)
        links = driver.find_elements(By.TAG_NAME, "a")

        for link in links:
            href = link.get_attribute("href")
            text = link.text.lower()
            if href:
                href_decoded = unquote(href.lower())
                if any(k in text or k in href_decoded for k in TERMS_KEYWORDS):
                    logging.info(f"📎 Found terms link: {href}")
                    return href
    except Exception as e:
        logging.error(f"[find_terms_link] {e}")
    return None

# 📄 Поиск PDF по ссылке
def detect_pdf_link(driver, url):
    try:
        driver.get(url)
        time.sleep(2)
        links = driver.find_elements(By.TAG_NAME, "a")

        for link in links:
            href = link.get_attribute("href")
            text = link.text.lower()
            if href and ".pdf" in href.lower():
                href_decoded = unquote(href.lower())
                if any(k in href_decoded or k in text for k in TERMS_KEYWORDS):
                    logging.info(f"📄 Found PDF link: {href}")
                    return href
    except Exception as e:
        logging.error(f"[detect_pdf_link] {e}")
    return None

# 🧾 Загрузка и извлечение PDF
def download_and_extract_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
        with open("terms.pdf", "wb") as f:
            f.write(response.content)
        return clean_text(extract_text("terms.pdf"))
    except Exception as e:
        logging.error(f"[PDF extract error] {e}")
        return ""

# 📰 Извлечение текста из HTML
def extract_text_from_html(driver, url):
    try:
        driver.get(url)
        time.sleep(2)
        body = driver.find_element(By.TAG_NAME, "body")
        return clean_text(body.text)
    except Exception as e:
        logging.error(f"[HTML extract error] {e}")
        return ""

# 🔁 Основная логика
def extract_terms(homepage_url):
    driver = get_driver()
    try:
        logging.info(f"🚀 Starting extraction from {homepage_url}")
        terms_url = find_terms_link(driver, homepage_url)
        if not terms_url:
            logging.warning("⚠️ No terms link found")
            return ""

        pdf_url = detect_pdf_link(driver, terms_url)
        if pdf_url:
            return download_and_extract_pdf(pdf_url)
        else:
            return extract_text_from_html(driver, terms_url)
    finally:
        driver.quit()

# 🚀 Flask App
app = Flask(__name__)

@app.route("/")
def hello():
    return "Selenium scraper is alive!"

@app.route("/extract-text")
def extract_text_route():
    try:
        homepage = "https://www.martessport.eu/cz"
        text = extract_terms(homepage)
        return jsonify({
            "status": "ok",
            "text_sample": text[:300]
        })
    except Exception as e:
        logging.exception("[extract_text_route]")
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
