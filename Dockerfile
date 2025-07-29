FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates fonts-liberation \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 \
    libxss1 libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libgbm1 libgtk-3-0 libu2f-udev libvulkan1 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install webdriver-manager

CMD ["python", "scraper.py"]
