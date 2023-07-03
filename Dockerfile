# Start from a Python 3.9 image.
FROM python:3.8.10

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory.
WORKDIR /code

# Install dependencies.
COPY . /code/
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000


# Run Django
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

