FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir /music
VOLUME /music

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]