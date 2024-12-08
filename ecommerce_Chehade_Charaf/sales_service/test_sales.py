# tests/test_sales.py

import pytest
from unittest.mock import patch
from models import Goods, Purchase
from database import db
from datetime import datetime, timezone

# Helper class for mocking POST responses
class MockPostResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json


def test_make_purchase_success(client, create_token, app):
    """
    Tests the /purchase endpoint for a successful purchase.
    """
    token = create_token('buyer1')
    sale_data = {
        'goods_id': 1,
        'quantity': 1
    }

    # Insert a Goods entry into the database
    with app.app_context():
        goods = Goods(
            id=1,
            name='Laptop',
            category='Electronics',
            price_per_item=999.99,
            description='A high-performance laptop.',
            stock_count=5
        )
        db.session.add(goods)
        db.session.commit()

    # Mock Customer Service to confirm sufficient funds
    def mock_customer_deduct(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self._json = json_data
                self.status_code = status_code

            def json(self):
                return self._json

        return MockResponse({'message': 'Balance deducted successfully'}, 200)

    with patch('resources.sales.requests.post', side_effect=mock_customer_deduct):
        response = client.post(
            '/purchase',
            headers={'Authorization': f'Bearer {token}'},
            json=sale_data
        )

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Purchase successful'
    assert 'purchase' in data
    assert data['purchase']['username'] == 'buyer1'
    assert data['purchase']['goods_id'] == 1
    assert data['purchase']['quantity'] == 1
    assert data['purchase']['total_price'] == 999.99

    # Verify the purchase is recorded in the database
    with app.app_context():
        purchase = Purchase.query.filter_by(username='buyer1', goods_id=1).first()
        assert purchase is not None
        assert purchase.quantity == 1
        assert purchase.total_price == 999.99


def test_make_purchase_insufficient_stock(client, create_token, app):
    """
    Tests the /purchase endpoint when the goods are out of stock.
    """
    token = create_token('buyer2')
    sale_data = {
        'goods_id': 2,
        'quantity': 3
    }

    # Insert a Goods entry with insufficient stock
    with app.app_context():
        goods = Goods(
            id=2,
            name='Smartphone',
            category='Electronics',
            price_per_item=499.99,
            description='A latest model smartphone.',
            stock_count=2  # Only 2 in stock
        )
        db.session.add(goods)
        db.session.commit()

    with patch('resources.sales.requests.post') as mock_post:
        response = client.post(
            '/purchase',
            headers={'Authorization': f'Bearer {token}'},
            json=sale_data
        )

    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Insufficient stock'


def test_make_purchase_insufficient_funds(client, create_token, app):
    """
    Tests the /purchase endpoint when the customer has insufficient funds.
    """
    token = create_token('buyer3')
    sale_data = {
        'goods_id': 3,
        'quantity': 2
    }

    # Insert a Goods entry
    with app.app_context():
        goods = Goods(
            id=3,
            name='Headphones',
            category='Electronics',
            price_per_item=199.99,
            description='Noise-cancelling headphones.',
            stock_count=10
        )
        db.session.add(goods)
        db.session.commit()

    # Mock Customer Service to simulate insufficient funds
    def mock_customer_insufficient(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self._json = json_data
                self.status_code = status_code

            def json(self):
                return self._json

        return MockResponse({'message': 'Insufficient funds'}, 400)

    with patch('resources.sales.requests.post', side_effect=mock_customer_insufficient):
        response = client.post(
            '/purchase',
            headers={'Authorization': f'Bearer {token}'},
            json=sale_data
        )

    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Failed to deduct balance'
    assert 'details' in data
    assert data['details']['message'] == 'Insufficient funds'


def test_get_purchase_history(client, create_token, app):
    """
    Tests the /purchase-history/<username> endpoint.
    """
    token = create_token('buyer4')

    # Insert mock purchase data into the database
    with app.app_context():
        # Insert corresponding Goods entries for purchases
        goods1 = Goods(
            id=4,
            name='Tablet',
            category='Electronics',
            price_per_item=149.99,
            description='A lightweight tablet.',
            stock_count=10
        )
        goods2 = Goods(
            id=5,
            name='Smartwatch',
            category='Electronics',
            price_per_item=199.99,
            description='A smartwatch with various features.',
            stock_count=5
        )
        db.session.add_all([goods1, goods2])
        db.session.commit()

        purchase1 = Purchase(
            username='buyer4',
            goods_id=4,
            quantity=2,
            total_price=299.98,
            purchase_date=datetime.now(timezone.utc)  # Use timezone-aware datetime
        )
        purchase2 = Purchase(
            username='buyer4',
            goods_id=5,
            quantity=1,
            total_price=199.99,
            purchase_date=datetime.now(timezone.utc)  # Use timezone-aware datetime
        )
        db.session.add_all([purchase1, purchase2])
        db.session.commit()

        # Prepare expected_purchases within the context
        expected_purchases = [
            {
                'id': purchase1.id,
                'username': 'buyer4',
                'goods_id': 4,
                'quantity': 2,
                'total_price': 299.98,
                'purchase_date': purchase1.purchase_date.isoformat()
            },
            {
                'id': purchase2.id,
                'username': 'buyer4',
                'goods_id': 5,
                'quantity': 1,
                'total_price': 199.99,
                'purchase_date': purchase2.purchase_date.isoformat()
            }
        ]

    response = client.get(
        '/purchase-history/buyer4',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    # Sorting to ensure order doesn't affect the test
    assert sorted(data['purchase_history'], key=lambda x: x['id']) == sorted(expected_purchases, key=lambda x: x['id'])


def test_purchase_history_unauthorized_access(client, create_token, app):
    """
    Tests the /purchase-history/<username> endpoint when accessing another user's history.
    """
    token = create_token('buyer5')

    response = client.get(
        '/purchase-history/buyer6',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'
