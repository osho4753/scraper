# Dockerfile в папке ./scraper
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Если ваш скрейпер запускается как скрипт
CMD ["python", "scraper.py"]
# Или если это Flask/FastAPI приложение
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "your_app:app"]