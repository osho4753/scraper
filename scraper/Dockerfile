FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scraper.py .

ENV PORT=3000

EXPOSE 3000

CMD ["python", "scraper.py"]
