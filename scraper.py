import os
import re
import logging
import sys
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from pdfminer.high_level import extract_text
from flask import Flask, jsonify

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s*\n\s*', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def download_and_extract_pdf(pdf_url):
    try:
        logging.info(f"📄 Downloading PDF: {pdf_url}")
        response = requests.get(pdf_url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        with open("terms.pdf", "wb") as f:
            f.write(response.content)

        text = extract_text("terms.pdf")
        return clean_text(text)
    except Exception as e:
        logging.error(f"[PDF extract error] {e}")
        return ""

def extract_text_from_html(url):
    try:
        logging.info(f"🌐 Fetching HTML: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        main = soup.find("main") or soup.find("body")
        if not main:
            return ""

        for tag in main.find_all(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = main.get_text(separator="\n", strip=True)
        return clean_text(text)
    except Exception as e:
        logging.error(f"[HTML extract error] {e}")
        return ""

def find_terms_link(homepage_url):
    try:
        response = requests.get(homepage_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a", href=True):
            text = a.get_text().lower()
            href = unquote(a["href"].lower())

            if any(k in text or k in href for k in TERMS_KEYWORDS):
                return urljoin(homepage_url, href)
    except Exception as e:
        logging.error(f"[find_terms_link] {e}")
    return None

def detect_pdf_link(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = unquote(a["href"].lower())
            text = a.get_text().lower()

            if ".pdf" in href and any(k in href or k in text for k in TERMS_KEYWORDS):
                return urljoin(url, href)
    except Exception as e:
        logging.error(f"[detect_pdf_link] {e}")
    return None

def extract_terms(homepage_url):
    try:
        logging.info(f"🚀 Starting extraction from {homepage_url}")
        terms_url = find_terms_link(homepage_url)
        if not terms_url:
            logging.warning("No terms link found")
            return ""

        logging.info(f"📎 Found terms link: {terms_url}")
        pdf_url = detect_pdf_link(terms_url)

        if pdf_url:
            return download_and_extract_pdf(pdf_url)
        else:
            return extract_text_from_html(terms_url)

    except Exception as e:
        logging.error(f"[extract_terms] {e}")
        return ""

# Flask App
app = Flask(__name__)

@app.route("/")
def hello():
    return "Parser is alive!"

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
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 3000))
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logging.error(f"[Flask] {e}")
