# Stable image that already includes Chromium/Firefox/WebKit and all deps
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

# Copy and install backend deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (Make sure requirements.txt includes:)
# beautifulsoup4
# lxml
# playwright

# Copy project
COPY . .

EXPOSE 8000

# Dev-friendly default; prod will override in compose.prod.yml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
