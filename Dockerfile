FROM python:3.11

# Установка wget, unzip и Java для selenium server (если нужен)
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y wget unzip openjdk-11-jre-headless

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scraper.py .

# Скачиваем selenium standalone chrome сервер (пример, уточни версию)
RUN wget https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.8.0/selenium-server-4.8.0.jar

# Копируем скрипт запуска
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 4444 3000

CMD ["./entrypoint.sh"]
