FROM python:3.12-slim

ENV PYTHONWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -e .

EXPOSE 5000

CMD ["python", "application.py"]