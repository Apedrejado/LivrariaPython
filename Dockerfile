FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app
COPY init.sql .

VOLUME ["/data", "/backups", "/exports"]

CMD ["python", "app/main.py"]
