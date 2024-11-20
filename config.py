import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '0987654321')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
