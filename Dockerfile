# Dockerfile в корне проекта

# Начинаем с образа Selenium, который уже содержит Chrome и Selenium Server
FROM selenium/standalone-chrome:latest

# Устанавливаем Python и pip, необходимые для вашего скрейпера
# Используем apt-get из Debian, так как базовый образ Selenium основан на Debian
USER root
# ...
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    # Эти пакеты чаще всего нужны для работы Python библиотек (например, Pillow для изображений)
    libjpeg-dev \
    zlib1g-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
# ...
RUN mkdir -p /var/log/supervisor

USER seluser

WORKDIR /home/seluser/app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]

