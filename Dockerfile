FROM python:3.11-slim

WORKDIR /app

# Copy everything
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p sitemaps

# Simple CMD
CMD ["python", "-m", "app.main"]
