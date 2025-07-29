FROM python:3.10-slim

# Установка зависимостей для Chrome и Selenium
RUN apt-get update && \
    apt-get install -y wget unzip gnupg2 curl ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 xdg-utils libgbm1 libgtk-3-0 && \
    rm -rf /var/lib/apt/lists/*

# Установка Google Chrome
RUN wget -q -O chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./chrome.deb && \
    rm chrome.deb

# Копируем проект
WORKDIR /app
COPY . .

# Устанавливаем Python-зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Запуск Flask-сервера
CMD ["python", "scraper.py"]
