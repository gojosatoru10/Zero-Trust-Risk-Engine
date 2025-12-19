# 1. Use the full Python image (Pre-includes C libraries like libgomp)
FROM python:3.12

# 2. Set the working directory
WORKDIR /app

# 3. Copy requirements and install python libraries
# We use --no-cache-dir to keep it clean, and increase timeout for slow networks
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# 4. Copy your application code and model files
COPY . .

# 5. Expose the port
EXPOSE 8000

# 6. Start the app
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]