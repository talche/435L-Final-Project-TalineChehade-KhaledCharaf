import os
from dotenv import load_dotenv
class Config:
    """
    Base configuration class for Flask application.
    """
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

class TestConfig(Config):
    """
    Testing configuration class for Flask application.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for tests
    JWT_SECRET_KEY = "test_secret_key"
