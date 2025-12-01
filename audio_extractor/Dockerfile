FROM python:3.9-slim

# CRITICAL: This line makes logs appear instantly in Datadog
ENV PYTHONUNBUFFERED=1

# Install system dependencies (FFmpeg is required for moviepy)
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the script directly
CMD ["python", "main.py"]