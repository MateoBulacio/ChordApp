FROM python:3.11-slim

WORKDIR /app

# Install system packages (needed for cs50 SQLite bindings)
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_PORT=5000
ENV SECRET_KEY=change-me

# Expose port for Traefik/other containers
EXPOSE 5000

CMD ["python", "app.py"]
