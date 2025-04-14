import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
config = {

    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:adgentes%40123@localhost:5432/shows'

}

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:adgentes%40123@localhost:5432/shows'
SQLALCHEMY_TRACK_MODIFICATIONS=False