# test_customer.py

import pytest
from app import app, db
from models import Customer

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_register_customer(client):
    response = client.post('/customers/register', json={
        'full_name': 'Alice Johnson',
        'username': 'alicej',
        'password': 'password123',
        'age': 25,
        'address': '789 Maple Ave',
        'gender': 'Female',
        'marital_status': 'Single'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['customer']['username'] == 'alicej'
    assert 'access_token' in data
