#!/bin/sh

# Change directory (./matsmart is mapped to /django i docker-compose.yml)
cd /django

# Load database and dummy data
python manage.py makemigrations                 # Get migrations from models
python manage.py migrate                        # Apply migrations to db
python manage.py loaddata initial_data.json     # Copy initial data to db
exec $@