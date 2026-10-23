FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Don't run as root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 5001

CMD ["gunicorn", "wsgi:app", "--workers", "4", "--bind", "0.0.0.0:5001", "--timeout", "120", "--access-logfile", "-"]
