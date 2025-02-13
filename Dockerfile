# Use a smaller base image to reduce size
FROM python:3.10-slim  

# Set working directory
WORKDIR /app  

# Copy only requirements first for efficient caching
COPY requirements.txt .  

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt  

# Copy the rest of the application files
COPY . .  

# Expose the port for FastAPI
EXPOSE 8000  

ENV AIPROXY_TOKEN=${AIPROXY_TOKEN}

# Use a more efficient command with explicit workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

