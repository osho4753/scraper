# Dockerfile в корне проекта

# Начинаем с образа Selenium, который уже содержит Chrome и Selenium Server
FROM selenium/standalone-chrome:latest

# Устанавливаем Python и pip, необходимые для вашего скрейпера
# Используем apt-get из Debian, так как базовый образ Selenium основан на Debian
USER root
# ...
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    supervisor \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxshmfence1 \
    libgbm1 \
    libgtk-3-0 \
    xdg-utils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/log/supervisor

USER seluser

WORKDIR /home/seluser/app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]

