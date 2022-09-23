# Tell Docker to use Python 3.8 
FROM python:3.8-slim-buster

# Set environment variables
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Set working directory (namechange for clarity)
WORKDIR /setup

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Run entrypoint script (populates database with admin account and some initial recipes)
COPY django-entrypoint.sh .
RUN chmod +x django-entrypoint.sh
ENTRYPOINT ["sh", "./django-entrypoint.sh" ]