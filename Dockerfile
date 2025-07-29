FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    libxss1 libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libgbm1 libgtk-3-0 libu2f-udev libvulkan1 fonts-liberation \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN wget -q -O chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./chrome.deb && rm chrome.deb

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install webdriver-manager

CMD ["python", "scraper.py"]
