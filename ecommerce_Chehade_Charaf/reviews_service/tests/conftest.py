# tests/conftest.py

import pytest
import sys
import os

# Step 1: Adjust the Python path to include the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app
from config import TestConfig
from database import db
from flask_jwt_extended import create_access_token


@pytest.fixture(scope='session')
def app():
    """
    Create and configure a new app instance for each test session.
    """
    # Initialize the app with TestConfig
    app = create_app(config_object=TestConfig)

    # Print app configuration for debugging
    print("App configuration:", app.config)

    # Establish an application context
    with app.app_context():
        db.create_all()  # Create all tables
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='session')
def client(app):
    """
    A test client for the app.
    """
    return app.test_client()


@pytest.fixture
def create_token(app):
    """
    Utility function to generate a JWT token for authentication in tests.
    Accepts a username and returns a JWT token with that identity.
    """

    def _create_token(username):
        """
        Generates a JWT token for the given username.

        Args:
            username (str): The username to include in the JWT token.

        Returns:
            str: A JWT token as a string.
        """
        with app.app_context():
            return create_access_token(identity=username)

    return _create_token
