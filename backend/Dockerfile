FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose ports that might be used
EXPOSE 8000 50051 50052 50053

# Use entrypoint to run migrations then start app
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command (overridden by docker-compose for microservices)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
