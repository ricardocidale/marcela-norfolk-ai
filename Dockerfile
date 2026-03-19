FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY voice_server.py .
COPY server.py .

EXPOSE 8080

CMD ["python", "voice_server.py"]
