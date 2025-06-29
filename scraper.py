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


TERMS_KEYWORDS = [
    "aktuální obchodní podmínky",
    "obchodní podmínky",
    "prodejní podmínky",
    "podmínky prodeje",
    "všeobecné obchodní podmínky",
    "terms and conditions",
    "general terms",
    "obchodni_podminky",
    "všeobecné prodejní podmínky"
]


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def init_driver():
    options = Options()

    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = webdriver.Chrome(options=options)

    return driver

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

        if any(keyword in combined for keyword in TERMS_KEYWORDS):
            return url
    return None

def download_and_extract_pdf(pdf_url):
    response = requests.get(pdf_url, timeout=10, headers=HEADERS)
    response.raise_for_status()

    filename = "terms_and_conditions.pdf"

    with open(filename, "wb") as f:
        f.write(response.content)

    text = extract_text(filename)

    save_to_file(text, "terms_and_conditions.txt")

    print("✅ terms_and_conditions.txt")
    return text

def extract_text_from_html(driver):
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//body"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")

    candidates = []

    main = soup.find("main")
    if main:
        candidates.append(main)

    for div in soup.find_all("div", class_=True):
        class_names = " ".join(div.get("class")).lower()

        if any(kw in class_names for kw in ["content", "text", "terms", "article"]):
            candidates.append(div)
            print(f"Found div with class: {div}")

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

    save_to_file(final_text, "terms_and_conditions.txt")

    print("✅ terms_and_conditions.txt")
    return final_text


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

def save_to_file(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def extract_terms(driver, homepage_url):
    driver.get(homepage_url)
    driver.set_window_size(1600, 1900)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    terms_url = find_terms_link(driver, homepage_url)

    if not terms_url:
        print("❌ There is no T&C link on the homepage.")
        return

    driver.get(terms_url)
    time.sleep(5)

    pdf_url = detect_pdf_link(driver, terms_url)

    if pdf_url:
        return download_and_extract_pdf(pdf_url)
    else:
        return extract_text_from_html(driver)

def main(homepage):
    driver = init_driver()

    try:
        extract_terms(driver, homepage)
    except Exception as e:
        print(f"[Error] {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape terms and conditions from a given URL.")
    parser.add_argument('url', metavar='URL', type=str)
    args = parser.parse_args()

    main(args.url)
