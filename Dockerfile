FROM python:3.10-slim

RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install webdriver-manager

CMD ["python", "scraper.py"]
