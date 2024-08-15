# Use the official Python image as the base image
FROM python:3.10.7-slim

# Set environment variables
ENV DJANGO_SECRET='sk-proj-IEw85unHcNEsKkWwS02aT3BlbkFJVNannmLs1LQ802GfRW4T'
ENV DB_CONN='postgresql://postgres:BjevCopvcFLhrWFhfbwVpChwCWXxLLoH@monorail.proxy.rlwy.net:49974/railway'
ENV OPENAI_API_KEY='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'

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip

# Install Google Chrome
RUN apt-get update && apt-get install -y wget gnupg

# Add Google Chrome repository and install
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# Verify Chrome installation
RUN google-chrome --version

RUN echo 'copying files'


COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput
# Expose the port that the app runs on
EXPOSE 8000

# Start the Django application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "linkedin.wsgi:application", "--timeout", "600"]
