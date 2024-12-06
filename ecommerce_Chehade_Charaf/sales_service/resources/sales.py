from flask_restful import Resource
from flask import request
from models import Goods, Purchase
from schemas import PurchaseSchema
from database import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from memory_profiler import profile  # Import the profile decorator

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

        # Get the goods item
        goods = Goods.query.get(goods_id)
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

        response = requests.post(customer_service_url, json=payload, headers=headers)
        if response.status_code != 200:
            return {'message': 'Failed to deduct balance', 'details': response.json()}, 400

        # Update goods stock count
        goods.stock_count -= quantity
        db.session.add(goods)

        # Record the purchase
        purchase = Purchase(
            username=username,
            goods_id=goods_id,
            quantity=quantity,
            total_price=total_price,
            purchase_date=datetime.utcnow()
        )
        db.session.add(purchase)
        db.session.commit()

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

        purchases = Purchase.query.filter_by(username=username).all()
        result = purchase_list_schema.dump(purchases)
        return {'purchase_history': result}, 200
