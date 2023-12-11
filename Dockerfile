# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /code/
RUN python manage.py collectstatic --no-input
RUN python manage.py migrate
RUN chown -R nobody:nogroup /code/
USER nobody
CMD gunicorn zrok_django_radial_calendar.wsgi:application --bind 0.0.0.0:8001
