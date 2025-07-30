# Dockerfile в корне проекта

# Начинаем с образа Selenium, который уже содержит Chrome и Selenium Server
FROM selenium/standalone-chrome:latest

# Устанавливаем Python и pip, необходимые для вашего скрейпера
# Используем apt-get из Debian, так как базовый образ Selenium основан на Debian
USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    # Добавляем зависимости, которые могут быть нужны для pdfminer или requests
    # libjpeg-dev и zlib1g-dev часто нужны для обработки изображений/PDF в Python
    # build-essential для компиляции некоторых Python пакетов
    libjpeg-dev \
    zlib1g-dev \
    build-essential \
    # Дополнительные зависимости для Flask
    # libffi-dev для cryptography, часто требуется для requests/Flask security
    libffi-dev \
    libssl-dev \
     fonts-liberation \
     libasound2 \
     libatk-bridge2.0-0 \
     libatk1.0-0 \
     libcairo2 \
     libcups2 \
     libdbus-1-3 \
     libexpat1 \
     libfontconfig1 \
     libgbm1 \
     libgdk-pixbuf2.0-0 \
     libglib2.0-0 \
     libgtk-3-0 \
     libnspr4 \
     libnss3 \
     libpango-1.0-0 \
     libpangocairo-1.0-0 \
     libxcomposite1 \
     libxdamage1 \
     libxext6 \
     libxfixes3 \
     libxkbcommon0 \
     libxrandr2 \
     libxrender1 \
     libxshmfence6 \
     libxtst6 \
     lsb-release \
     xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Переключаемся обратно на пользователя Selenium, чтобы не запускать как root
# Это хорошая практика безопасности, но может вызвать проблемы с правами
# Если столкнетесь с ошибками, временно закомментируйте эту строку
USER seluser

WORKDIR /home/seluser/app

# Копируем requirements.txt и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем ваше Flask-приложение и скрейпер
# Предполагается, что scraper.py и все связанные файлы Flask находятся в корне
COPY . .

# Открываем порт для Flask-приложения
EXPOSE 3000

# Запускаем Selenium Standalone Server в фоновом режиме
# и затем ваше Flask-приложение.
# Это критически важная часть. Мы используем CMD,
# который запускает Selenium Server и затем ваше Flask-приложение
# Selenium Standalone Server запускается по умолчанию при старте образа selenium/standalone-chrome:latest.
# Нам нужно убедиться, что он запущен до нашего Flask-приложения.
# Обычно он уже запускается командой ENTRYPOINT в базовом образе Selenium.
# Нам нужно переопределить CMD/ENTRYPOINT, чтобы добавить запуск нашего Flask-приложения.

# Option 1: Использовать supervisord или S6-overlay (сложнее, но надежнее для нескольких процессов)
# Option 2: Запустить Selenium в фоне и затем ваше приложение (проще, но может быть менее надежно)

# Давайте попробуем более простой подход: Selenium уже стартует в фоновом режиме
# благодаря ENTRYPOINT в образе selenium/standalone-chrome.
# Нам нужно убедиться, что он успел запуститься, прежде чем наш скрипт к нему обратится.
# Основной командой контейнера будет запуск вашего Flask-приложения.

# Selenium server запускается командой ENTRYPOINT, а CMD в базовом образе - это exec /opt/bin/entry_point.sh
# Нам нужно переопределить CMD, чтобы Selenium все еще запускался.
# Наиболее надежный способ - скопировать entry_point.sh и добавить свой запуск.
# Но для простоты попробуем использовать `supervisord` или запустить скрипт, который ждет Selenium.

# Простой, но потенциально менее надежный способ:
# Запускаем Flask-приложение. Предполагается, что Selenium уже запущен благодаря ENTRYPOINT базового образа.
# Возможно, потребуется задержка в Python-коде перед первым обращением к Selenium.
# Если ваш Flask-файл называется scraper.py, и ваше приложение называется 'app'
CMD ["python3", "scraper.py"]

# Если вы используете Gunicorn, что лучше для продакшена:
# CMD ["gunicorn", "--bind", "0.0.0.0:3000", "scraper:app"]