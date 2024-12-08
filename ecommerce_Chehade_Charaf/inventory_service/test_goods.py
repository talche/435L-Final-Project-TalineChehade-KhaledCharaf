import pytest
from models import Goods
from flask import jsonify


# Test getting the list of goods
def test_get_goods_list(client):
    response = client.get('/goods')
    assert response.status_code == 200
    data = response.get_json()
    assert 'goods' in data
    assert isinstance(data['goods'], list)


# Test adding a new good
def test_add_good(client):
    new_good = {
        'name': 'Test Good',
        'category': 'food',
        'price_per_item': 50.0,
        'description': 'This is a test good',
        'stock_count': 100
    }

    response = client.post('/goods', json=new_good)
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Goods added'
    assert data['goods']['name'] == 'Test Good'


# Test adding a good with invalid data (missing fields)
def test_add_good_invalid_data(client):
    invalid_good = {
        'name': 'Invalid Good',
        'category': 'Invalid Category',
        'price_per_item': 'invalid_price',  # Invalid data type
        'stock_count': 100
    }

    response = client.post('/goods', json=invalid_good)
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Validation errors'


# Test retrieving a specific good by ID
def test_get_good_by_id(client):
    # Add a new good first
    new_good = {
        'name': 'Good By ID',
        'category': 'Test Category',
        'price_per_item': 30.0,
        'description': 'Good for testing get by ID',
        'stock_count': 50
    }
    


