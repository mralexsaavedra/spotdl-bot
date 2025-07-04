FROM python:3.10-alpine

RUN apk add --no-cache ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /music /cache

ENV RUNNING_IN_DOCKER=true
ENV DOWNLOAD_DIR="/music"
ENV CACHE_DIR="/app/cache"
ENV LOCALE_DIR="/app/locale"
ENV LOG_DIR="/app/logs"
ENV LOG_LEVEL="INFO"

CMD ["python", "main.py"]