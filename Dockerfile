FROM python:3.10-alpine

LABEL maintainer="mralexsaavedra" \
  version="1.0" \
  description="SpotDL Telegram Bot Docker image"

RUN apk add --no-cache ffmpeg

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf ~/.cache/pip

COPY . .

ENV RUNNING_IN_DOCKER=true \
  DOWNLOAD_DIR="/music" \
  CACHE_DIR="/app/cache" \
  LOCALE_DIR="/app/locale" \
  LOG_DIR="/app/logs" \
  LOG_LEVEL="INFO"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD pgrep -f main.py || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "main.py"]