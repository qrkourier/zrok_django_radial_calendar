# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

ARG PUID=2171
ARG PGID=2171

ARG ZROK_PY_NAME=zrok

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
RUN apt-get -y update \
    && apt-get -y install \
        git \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt --extra-index-url=https://test.pypi.org/simple/

# Copy project
COPY . /code/
RUN python manage.py collectstatic --no-input
RUN python manage.py migrate
RUN chown -R ${PUID}:${PGID} /code/
USER ${PGID}
