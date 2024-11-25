import os
from datetime import timedelta
import secrets

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', "0987654321") 

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_TOKEN_LOCATION = ['cookies']

    JWT_ACCESS_COOKIE_NAME = 'token'

    JWT_COOKIE_CSRF_PROTECT = False

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', "0987654321")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30) 

