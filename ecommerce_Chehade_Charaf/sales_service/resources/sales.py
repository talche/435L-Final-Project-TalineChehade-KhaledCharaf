import pybreaker
from flask_restful import Resource
from flask import request
from models import Goods, Purchase
from schemas import PurchaseSchema
from database import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from memory_profiler import profile  # Import the profile decorator

# Create the circuit breaker object
breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)  # Fail after 3 failures, reset after 30 seconds

purchase_schema = PurchaseSchema()
purchase_list_schema = PurchaseSchema(many=True)

def is_admin(username):
    """
    Check if the given username belongs to an admin.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the user is 'admin', False otherwise.
    """
    return username == 'admin'


class PurchaseResource(Resource):
    """
    Resource for handling purchase operations.
    """

    @profile  # Memory profiler decorator
    @jwt_required()
    def post(self):
        """
        Handle POST requests to create a new purchase.

        Expects JSON data with 'goods_id' and 'quantity'.

        Returns:
            tuple: A tuple containing a JSON response and HTTP status code.
        """
        data = request.get_json()
        errors = purchase_schema.validate(data)
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, 400

        username = get_jwt_identity()
        goods_id = data['goods_id']
        quantity = data['quantity']

        try:
            # Wrap database operation with the circuit breaker
            goods = breaker.call(lambda: Goods.query.get(goods_id))
        except pybreaker.CircuitBreakerError:
            return {'message': 'Service unavailable, please try again later'}, 503

        if not goods:
            return {'message': 'Goods not found'}, 404

        if goods.stock_count < quantity:
            return {'message': 'Insufficient stock'}, 400

        total_price = goods.price_per_item * quantity

        # Deduct from customer's wallet balance via Customers Service
        customer_service_url = 'http://localhost:8001/customers/deduct-balance'
        payload = {
            'username': username,
            'amount': total_price
        }
        jwt_token = request.headers.get('Authorization').split(' ')[1]
        headers = {
            'Authorization': f'Bearer {jwt_token}'  # Include the JWT token
        }

        try:
            response = breaker.call(lambda: requests.post(customer_service_url, json=payload, headers=headers))
        except pybreaker.CircuitBreakerError:
            return {'message': 'Failed to communicate with customer service. Please try again later.'}, 503

        if response.status_code != 200:
            return {'message': 'Failed to deduct balance', 'details': response.json()}, 400

        # Update goods stock count
        goods.stock_count -= quantity
        try:
            breaker.call(lambda: db.session.add(goods))
            breaker.call(lambda: db.session.commit())
        except pybreaker.CircuitBreakerError:
            return {'message': 'Service unavailable, please try again later'}, 503

        # Record the purchase
        purchase = Purchase(
            username=username,
            goods_id=goods_id,
            quantity=quantity,
            total_price=total_price,
            purchase_date=datetime.utcnow()
        )

        try:
            breaker.call(lambda: db.session.add(purchase))
            breaker.call(lambda: db.session.commit())
        except pybreaker.CircuitBreakerError:
            return {'message': 'Failed to record the purchase. Please try again later.'}, 503

        result = purchase_schema.dump(purchase)
        return {'message': 'Purchase successful', 'purchase': result}, 201


class PurchaseHistoryResource(Resource):
    """
    Resource for handling retrieval of purchase history.
    """

    @profile
    @jwt_required()
    def get(self, username):
        """
        Handle GET requests to retrieve purchase history for a user.

        Args:
            username (str): The username whose purchase history is to be retrieved.

        Returns:
            tuple: A tuple containing a JSON response and HTTP status code.
        """
        current_user = get_jwt_identity()
        if current_user != username:
            return {'message': 'Unauthorized access'}, 403

        try:
            # Wrap database query for purchase history with circuit breaker
            purchases = breaker.call(lambda: Purchase.query.filter_by(username=username).all())
        except pybreaker.CircuitBreakerError:
            return {'message': 'Service unavailable, please try again later'}, 503

        result = purchase_list_schema.dump(purchases)
        return {'purchase_history': result}, 200
