#!/bin/bash

java -jar selenium-server-4.8.0.jar standalone &

echo "Waiting for selenium to start..."
while ! curl -s http://localhost:4444/status > /dev/null; do
  sleep 1
done

# Запускаем твой скрапер (предполагается, что он слушает 3000)
python scraper.py
