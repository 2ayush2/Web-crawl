# Use Python 3.9 slim image
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt ./

# Install dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and data to the container
COPY ./myapp /app/myapp
COPY ./data /app/data
COPY ./static /app/static
COPY ./templates /app/templates

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Start FastAPI app with Uvicorn
CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
