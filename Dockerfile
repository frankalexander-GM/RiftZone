FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir flask-socketio eventlet python-dotenv

COPY . .

EXPOSE 5050

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5050/ || exit 1

CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5050", "--worker-connections", "1000", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
