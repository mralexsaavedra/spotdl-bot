FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apk add --no-cache ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /music
VOLUME /music

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]