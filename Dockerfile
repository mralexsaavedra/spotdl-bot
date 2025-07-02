FROM python:3.10-alpine

RUN apk add --no-cache ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /music /cache

CMD ["python", "main.py"]
