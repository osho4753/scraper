FROM cypress/browsers:node-22.17.1-chrome-138.0.7204.157-1-ff-140.0.4-edge-138.0.3351.83-1
RUN apt-get update && apt-get install -y python3 python3-pip
RUN echo $(python3 -m site --user-base)
COPY requirements.txt .
ENV PATH=/root/.local/bin:$PATH
RUN apt-get update && apt-get install -y python3-venv python3-pip && \
    python3 -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["/app/venv/bin/python", "scraper.py"]
