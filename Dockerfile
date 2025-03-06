FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add the app directory to PYTHONPATH
ENV PYTHONPATH=/app