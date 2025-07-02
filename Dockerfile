FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /music
RUN mkdir -p /data

CMD ["python", "main.py"]