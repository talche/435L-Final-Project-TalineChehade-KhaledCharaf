import pytest
from models import Customer
from database import db
from flask_jwt_extended import create_access_token

# Helper function to create a customer token for authentication
def create_token_for_customer(username):
    customer = Customer.query.filter_by(username=username).first()
    return create_access_token(identity=customer.username)

# Test registration of a new customer
def test_customer_register(client):
    register_data = {
        'full_name': 'John Doe',
        'username': 'johndoe',
        'password': 'password123',
        'age': 30,
        'address': '123 Main St',
        'gender': 'Male',
        'marital_status': 'Single'
    }

    response = client.post('/customers/register', json=register_data)

    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Customer registered'
    assert 'access_token' in data
    assert data['customer']['username'] == 'johndoe'

# Test that trying to register a customer with an existing username returns an error
def test_customer_register_existing_username(client):
    # First, create a customer
    register_data = {
        'full_name': 'Jane Doe',
        'username': 'janedoe',
        'password': 'password123',
        'age': 28,
        'address': '456 Elm St',
        'gender': 'Female',
        'marital_status': 'Married'
    }

    client.post('/customers/register', json=register_data)

    # Try registering again with the same username
    response = client.post('/customers/register', json=register_data)

    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Username already exists'

# Test retrieving a customer's details
def test_get_customer_details(client):
    # Create a customer token
    token = create_token_for_customer('johndoe')

    response = client.get(
        '/customers/johndoe',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['customer']['username'] == 'johndoe'

# Test that a user cannot access another user's data
def test_get_customer_details_unauthorized(client):
    # Create a customer token for a different user
    token = create_token_for_customer('janedoe')

    response = client.get(
        '/customers/johndoe',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'

# Test updating customer details
def test_update_customer_details(client):
    token = create_token_for_customer('johndoe')
    update_data = {
        'full_name': 'John Doe Updated',
        'age': 31,
        'address': '789 Oak St',
        'gender': 'Male',
        'marital_status': 'Married'
    }

    response = client.put(
        '/customers/johndoe',
        headers={'Authorization': f'Bearer {token}'},
        json=update_data
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Customer updated'
    assert data['customer']['full_name'] == 'John Doe Updated'
    assert data['customer']['age'] == 31

# Test that a user cannot update another user's data
def test_update_customer_details_unauthorized(client):
    token = create_token_for_customer('janedoe')
    update_data = {
        'full_name': 'Jane Doe Updated',
        'age': 29,
        'address': '456 Pine St',
        'gender': 'Female',
        'marital_status': 'Divorced'
    }

    response = client.put(
        '/customers/johndoe',
        headers={'Authorization': f'Bearer {token}'},
        json=update_data
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'

# Test deleting a customer
def test_delete_customer(client):
    # Register and create a customer
    register_data = {
        'full_name': 'Mark Smith',
        'username': 'marksmith',
        'password': 'password123',
        'age': 40,
        'address': '123 Maple St',
        'gender': 'Male',
        'marital_status': 'Single'
    }
    client.post('/customers/register', json=register_data)

    # Create a token for the customer to be deleted
    token = create_token_for_customer('marksmith')

    response = client.delete(
        '/customers/marksmith',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Customer deleted'

# Test that a user cannot delete another user's data
def test_delete_customer_unauthorized(client):
    # Create two customers
    register_data_1 = {
        'full_name': 'Emily Davis',
        'username': 'emilydavis',
        'password': 'password123',
        'age': 25,
        'address': '456 Birch St',
        'gender': 'Female',
        'marital_status': 'Single'
    }
    client.post('/customers/register', json=register_data_1)

    register_data_2 = {
        'full_name': 'Mike Brown',
        'username': 'mikebrown',
        'password': 'password123',
        'age': 35,
        'address': '789 Cedar St',
        'gender': 'Male',
        'marital_status': 'Married'
    }
    client.post('/customers/register', json=register_data_2)

    # Try deleting customer1 by customer2
    token = create_token_for_customer('mikebrown')

    response = client.delete(
        '/customers/emilydavis',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'


# Test balance deduction for a customer
def test_deduct_balance(client):
    # Register a customer
    customer_data = {
        'full_name': 'Anna Black',
        'username': 'annablack',
        'password': 'password123',
        'age': 30,
        'address': '456 Birch St',
        'gender': 'Female',
        'marital_status': 'Single'
    }

    # Register the customer
    response = client.post('/customers/register', json=customer_data)
    assert response.status_code == 201  # Ensure registration was successful

    # Create a token for the customer
    token = create_token_for_customer('annablack')

    # Set initial wallet balance to 100 for the customer (since the default is 0)
    customer = Customer.query.filter_by(username='annablack').first()
    customer.wallet_balance = 100  # Give a balance for testing
    db.session.commit()

    # Test valid balance deduction
    deduct_data = {'username': 'annablack', 'amount': 50}
    response = client.post(
        '/customers/deduct-balance',  # Ensure this path matches the actual route
        headers={'Authorization': f'Bearer {token}'},
        json=deduct_data
    )

    # Ensure the request was successful
    assert response.status_code == 200

    # Check the response data
    data = response.get_json()
    assert data['message'] == 'Balance deducted'
    assert data['new_balance'] == 50  # 100 - 50 = 50


# Test insufficient balance during deduction
def test_deduct_balance_insufficient(client):
    # Create a customer with insufficient balance
    customer_data = {
        'full_name': 'Sophia Green',
        'username': 'sophiagreen',
        'password': 'password123',
        'age': 35,
        'address': '123 Oak St',
        'gender': 'Female',
        'marital_status': 'Married'
    }

    client.post('/customers/register', json=customer_data)

    token = create_token_for_customer('sophiagreen')

    # Test invalid deduction (insufficient balance)
    deduct_data = {'username': 'sophiagreen', 'amount': 100}
    response = client.post(
        '/customers/deduct-balance',
        headers={'Authorization': f'Bearer {token}'},
        json=deduct_data
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Insufficient wallet balance'

# Test adding balance to a customer's wallet
def test_add_balance(client):
    customer_data = {
        'full_name': 'Liam Brown',
        'username': 'liambrown',
        'password': 'password123',
        'age': 27,
        'address': '789 Elm St',
        'gender': 'Male',
        'marital_status': 'Single'
    }

    client.post('/customers/register', json=customer_data)

    token = create_token_for_customer('liambrown')

    # Test valid balance addition
    add_data = {'username': 'liambrown', 'amount': 100}
    response = client.post(
        '/customers/add-balance',
        headers={'Authorization': f'Bearer {token}'},
        json=add_data
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Balance Added'
