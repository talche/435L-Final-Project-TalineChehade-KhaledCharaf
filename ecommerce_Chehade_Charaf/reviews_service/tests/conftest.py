# tests/conftest.py

import pytest
from app import app as flask_app
from database import db
from flask_jwt_extended import create_access_token
from models import Review
from datetime import datetime
import os
import sys
# Adjust the path to include the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test_secret_key",
    })

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def admin_token(app):
    """Generate a JWT token for an admin user."""
    with app.app_context():
        token = create_access_token(identity='admin')
        return token

@pytest.fixture
def user_token(app):
    """Generate a JWT token for a regular user."""
    with app.app_context():
        token = create_access_token(identity='user1')
        return token
