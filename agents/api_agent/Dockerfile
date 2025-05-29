# Use official Python image
FROM python:3.10

# Set work directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8001

# Run the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
