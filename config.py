import os

SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS=False
SECRET_KEY=os.getenv('SECRET')
DEBUG = True