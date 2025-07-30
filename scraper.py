try:
    import os
    import re
    import time
    import threading
    import logging
    import sys
    import requests

    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, unquote
    from pdfminer.high_level import extract_text

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager


    from flask import Flask, jsonify
    import subprocess
    logging.info(subprocess.getoutput("google-chrome-stable --version"))

except Exception as e:
    logging.error(f"[FATAL IMPORT ERROR] {e}")
    sys.exit(1)

# Логгинг
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

TERMS_KEYWORDS = [
    "aktuální obchodní podmínky", "obchodní podmínky", "obchodni-podminky",
    "prodejní podmínky", "podmínky prodeje", "všeobecné obchodní podmínky",
    "terms and conditions", "terms", "vop", "general terms",
    "obchodni_podminky", "všeobecné prodejní podmínky", "vše o nákupu"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Referer": "https://www.martessport.eu/cz",
    "Accept-Language": "cs-CZ,cs;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}

def init_driver():
    try:
        options = Options()
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2
        })
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--ignore-certificate-errors')

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={HEADERS['User-Agent']}")

        driver = webdriver.Chrome(ChromeDriverManager.install(),options=options)
        logging.info("Chrome WebDriver initialized")
        return driver
    except Exception as e:
        logging.error(f"[init_driver] Failed to initialize WebDriver: {e}")
        raise

def get_all_links(driver, homepage_url):
    try:
        a_tags = driver.find_elements(By.TAG_NAME, "a")
        links = []
        for a in a_tags:
            text = a.text.strip().lower()
            href = a.get_attribute("href")
            if href:
                full_url = urljoin(homepage_url, href)
                links.append((text, full_url))
        return links
    except Exception as e:
        logging.error(f"[get_all_links] {e}")
        return []

def find_terms_link(driver, homepage_url):
    try:
        links = get_all_links(driver, homepage_url)
        for text, url in links:
            combined = (text + " " + url).lower()
            if any(keyword in combined for keyword in TERMS_KEYWORDS):
                return url
        return None
    except Exception as e:
        logging.error(f"[find_terms_link] {e}")
        return None

def clean_text(text):
    if not text: return ""
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def download_and_extract_pdf(pdf_url, homepage_url):
    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get(pdf_url, stream=True, timeout=10)
        response.raise_for_status()
        with open("terms_and_conditions.pdf", "wb") as f:
            f.write(response.content)
        text = extract_text("terms_and_conditions.pdf")
        fin = clean_text(text)
        logging.info(fin[:150] if fin else f"❌ Empty PDF text from {homepage_url}")
        return fin
    except Exception as e:
        logging.error(f"[download_and_extract_pdf] {e}")
        return ""

def extract_text_from_html(driver, homepage_url):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        candidates = []

        main = soup.find("main")
        if main:
            logging.info("Found <main>")
            candidates.append(main)

        for div in soup.find_all("div", class_=True):
            class_names = " ".join(div.get("class")).lower()
            if any(kw in class_names for kw in ["content", "text", "terms", "article"]):
                candidates.append(div)

        if not candidates:
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
        fin = clean_text(final_text)
        logging.info(fin[:150] if fin else f"❌ Empty HTML text from {homepage_url}")
        return fin
    except Exception as e:
        logging.error(f"[extract_text_from_html] {e}")
        return ""

def detect_pdf_link(driver, base_url):
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip().lower()
            if not href: continue
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
    except Exception as e:
        logging.error(f"[detect_pdf_link] {e}")
        return None

def extract_terms(driver, homepage_url):
    try:
        try:
            response = requests.get("https://www.martessport.eu/cz",headers=headers, timeout=5)
            logging.info(f"[requests test] Status: {response.status_code}")
        except Exception as e:
            logging.error(f"[requests test] Failed: {e}")
        logging.info(f"[extract_terms] {homepage_url}")

        try:
            driver.get(homepage_url)
            logging.info(f"[extract_terms] Page length: {len(driver.page_source)}")
        except Exception as e:
            logging.error(f"[extract_terms] Failed to open URL: {e}")
            return        
        driver.set_window_size(1600, 1900)
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        logging.info(f"driver is in {homepage_url}")

        terms_url = find_terms_link(driver, homepage_url)
        if not terms_url:
            logging.info("❌ No T&C link found.")
            return
        logging.info(f"driver find {terms_url}")

        driver.get(terms_url)
        time.sleep(5)
        pdf_url = detect_pdf_link(driver, terms_url)
        logging.info(f"📄 PDF URL: {pdf_url}")

        if pdf_url:
            return download_and_extract_pdf(pdf_url, homepage_url)
        else:
            return extract_text_from_html(driver, homepage_url)

    except Exception as e:
        logging.error(f"[extract_terms] {e}")
        return ""

def main(homepage):
    try:
        driver = init_driver()
        try:
            driver = init_driver()
            extract_terms(driver, homepage)
        except Exception as e:
            logging.error(f"[main] {e}")
        finally:
            if driver:
                logging.info(f"[main] is done")

                driver.quit()
    except Exception as e:
        logging.error(f"[main] {e}")

# Flask app setup
app = Flask(__name__)

def run_scraper():
    try:
        print(">>> Scraper thread started")
        main('https://www.martessport.eu/cz')
        logging.info("Scraper finished.")
    except Exception as e:
        logging.error(f"[run_scraper] {e}")

@app.route("/")
def hello():
    return "Parser is alive!"

@app.route("/start-scraper")
def start_scraper():
    thread = threading.Thread(target=run_scraper)
    thread.start()
    return jsonify({"status": "scraper started"})

@app.route("/extract-text")
def extract_text_route():
    try:
        driver = init_driver()
        print(">>> Scraper thread started")

        text = extract_terms(driver, "https://www.martessport.eu/cz")
        driver.quit()
        return jsonify({"status": "ok", "text_sample": text[:300]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 3000))
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logging.error(f"[Flask] {e}")