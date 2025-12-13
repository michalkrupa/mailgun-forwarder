FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8765

CMD ["gunicorn", "--bind", "0.0.0.0:8765", "--workers", "4", "--timeout", "600", "--access-logfile", "-", "mailgun.app:app"]
