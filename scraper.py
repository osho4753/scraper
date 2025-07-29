import json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
import re
import time
import requests
from urllib.parse import urljoin, unquote
from pdfminer.high_level import extract_text
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, jsonify
import os
import threading
import logging
import sys

logging.basicConfig(
    stream=sys.stdout,   
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)
TERMS_KEYWORDS = [
    "aktuální obchodní podmínky",
    "obchodní podmínky",
    "obchodni-podminky",
    "prodejní podmínky",
    "podmínky prodeje",
    "všeobecné obchodní podmínky",
    "terms and conditions",
    "terms",
    "vop",
    "general terms",
    "obchodni_podminky",
    "všeobecné prodejní podmínky",
    "vše o nákupu"
]



HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driverPath = "/usr/bin/chromedriver"
    service = Service(driverPath)
    driver = webdriver.Chrome(service=service, options=options)

    logging.info("Chrome WebDriver initialized")
    return driver

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Referer": "https://www.marionnaud.cz/",
    "Accept": "application/pdf",
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "DNT": "1",  # Do Not Track
    "Upgrade-Insecure-Requests": "1",
}

def get_all_links(driver, homepage_url):
    links = []
    a_tags = driver.find_elements(By.TAG_NAME, "a")

    for a in a_tags:
        text = a.text.strip().lower()
        href = a.get_attribute("href")

        if href:
            full_url = urljoin(homepage_url, href)
            links.append((text, full_url))
    return links

def find_terms_link(driver, homepage_url):
    links = get_all_links(driver, homepage_url)
    
    for text, url in links:
        combined = (text + " " + url).lower()
        logging.info(combined)
        if any(keyword in combined for keyword in TERMS_KEYWORDS):
            return url
        
    return None

def clean_text(text):
    """Basic text cleaning: multiple newlines/spaces, strip."""
    if not text: return ""
    text = re.sub(r'\s*\n\s*', '\n', text)  # Collapse newlines with surrounding spaces to one newline
    text = re.sub(r'[ \t]+', ' ', text)      # Collapse multiple spaces/tabs to single space
    return text.strip()

def download_and_extract_pdf(pdf_url,homepage_url):
    session = requests.Session()
    session.headers.update(headers)
    response = requests.get(pdf_url, headers=headers,stream=True, verify=False, timeout=10)
    response.raise_for_status()

    filename = "terms_and_conditions.pdf"

    with open(filename, "wb") as f:
        f.write(response.content)

    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', homepage_url)
    text = extract_text(filename)
    fin = clean_text(text)
    if text:
        logging.info(fin[:150])
    else:
        logging.info(homepage_url, "errors.json")

    return fin

def extract_text_from_html(driver,homepage_url):
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//body"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")

    candidates = []

    main = soup.find("main")
    if main:
        logging.info('main')
        candidates.append(main)

    for div in soup.find_all("div", class_=True):
        class_names = " ".join(div.get("class")).lower()

        if any(kw in class_names for kw in ["content", "text", "terms", "article"]):
            candidates.append(div)
    if not candidates or main not in candidates or len(candidates) < 10:
        body = soup.find("body")

        if body:
            candidates.append(body)

    extracted_texts = []

    for section in candidates:

        for tag in section.find_all(["header", "footer", "nav", "aside", "script", "style"]):
            tag.decompose()

        text = section.get_text(separator="\n", strip=True)
        text = re.sub(r"\n{2,}", "\n\n", text)
        extracted_texts.append(text)

    final_text = "\n\n".join(extracted_texts)
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', homepage_url)
    fin = clean_text(final_text)

    if fin:
        logging.info(fin[:150])
    else:
        logging.info(homepage_url, "errors.json")

    return fin

def detect_pdf_link(driver, base_url):
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        text = link.text.strip().lower()

        if not href:
            continue

        decoded = unquote(href).lower()

        if href.startswith("javascript:") and ".pdf" in href:
            match = re.search(r"['\"](https?://[^'\"]+\.pdf)['\"]", href)

            if match:
                return match.group(1)
        elif ".pdf" in href.lower() and (
            any(k in decoded for k in TERMS_KEYWORDS) or any(k in text for k in TERMS_KEYWORDS)
        ):
            return urljoin(base_url, href)
        
    return None


def extract_terms(driver, homepage_url):
    driver.get(homepage_url)
    driver.set_window_size(1600, 1900)
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', homepage_url)
    time.sleep(2)


    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    terms_url = find_terms_link(driver, homepage_url)
    if not terms_url:
        logging.info("❌ There is no T&C link on the homepage.")
        return

    driver.get(terms_url)
    time.sleep(5)

    pdf_url = detect_pdf_link(driver, terms_url)


    logging.info(f"📄 PDF URL: {pdf_url}")

    if pdf_url or pdf_url:
        return download_and_extract_pdf(pdf_url,homepage_url)
    else:
        return extract_text_from_html(driver,homepage_url)
    
def main(homepage):
    driver = init_driver()

    try:
        extract_terms(driver, homepage)
    except Exception as e:
        logging.info(f"[Error] {e}")
    finally:
        driver.quit()


app = Flask(__name__)

def run_scraper():
    try:
        logging.info("Starting Selenium scraper...")

        main('https://www.mader.cz/')  
        logging.info("Selenium scraper finished successfully.")

    except Exception as e:
        logging.info(f"Error in scraper: {e}")

@app.route("/")
def hello():
    return "Parser is alive!"

@app.route("/start-scraper")
def start_scraper():
    thread = threading.Thread(target=run_scraper)
    thread.start()
    return jsonify({"status": "scraper started"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
