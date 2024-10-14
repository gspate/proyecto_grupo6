# Use a base image with Python
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Copy requirements file first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the rest of the application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the migrations and start the server with unbuffered logs
ENTRYPOINT ["sh", "-c"]
<<<<<<< HEAD
CMD ["python -u manage.py makemigrations && python -u manage.py migrate && python -u manage.py runserver 0.0.0.0:8000"]
=======
CMD ["python -u manage.py makemigrations && python -u manage.py migrate && gunicorn ApiBackDjango.wsgi:application --bind 0.0.0.0:8000"]
>>>>>>> main
