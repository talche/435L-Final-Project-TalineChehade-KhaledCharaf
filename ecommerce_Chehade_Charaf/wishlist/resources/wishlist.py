import pybreaker
from flask_restful import Resource
from flask import request, jsonify
from models import Wishlist
from database import db
from schemas import WishlistSchema
from sqlalchemy.exc import IntegrityError

# Initialize the circuit breaker
circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)  # Max 3 failures, reset after 60 seconds

# Initialize schemas
wishlist_schema = WishlistSchema()
wishlist_list_schema = WishlistSchema(many=True)

class WishlistResource(Resource):
    """
    Resource for managing individual wishlist items.
    Supports POST, GET, DELETE operations for adding, viewing, and removing items.
    """
    
    def post(self):
        """
        Handle POST request to add a new item to the wishlist.
        
        This method validates input data, checks for errors, and adds a new item to the wishlist. If the circuit breaker is triggered,
        it returns a service unavailable message.
        
        Returns:
            dict: A success message with the added item details or an error message if validation fails.
        """
        data = request.get_json()
        # Validate the data using the Wishlist schema
        errors = wishlist_schema.validate(data)
        if errors:
            return jsonify({'message': 'Validation errors', 'errors': errors}), 400

        new_item = Wishlist(
            customer_username=data['customer_username'],
            product_id=data['product_id']
        )

        try:
            # Use the circuit breaker to manage adding to the database
            circuit_breaker.call(db.session.add, new_item)
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return jsonify({'message': 'Circuit breaker triggered, unable to add item to wishlist'}), 503
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Product already in wishlist"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        # Serialize and return the new wishlist item
        result = wishlist_schema.dump(new_item)
        return jsonify({'message': 'Item added to wishlist', 'wishlist_item': result}), 201

    def get(self, customer_username):
        """
        Handle GET request to retrieve a specific user's wishlist.

        This method fetches a user's wishlist. If the circuit breaker is triggered, it returns a service unavailable message.
        
        Args:
            customer_username (str): The username of the customer whose wishlist to retrieve.

        Returns:
            dict: A list of wishlist items or an error message if the service is unavailable.
        """
        try:
            # Use circuit breaker to retrieve data
            items = circuit_breaker.call(Wishlist.query.filter_by, customer_username=customer_username).all()
        except pybreaker.CircuitBreakerError:
            return jsonify({'message': 'Circuit breaker triggered, unable to fetch wishlist'}), 503

        if not items:
            return jsonify({'message': 'Wishlist is empty'}), 404

        # Serialize and return the wishlist items
        result = wishlist_list_schema.dump(items)
        return jsonify({'wishlist': result}), 200

    def delete(self):
        """
        Handle DELETE request to remove a product from the wishlist.

        This method deletes the specified product from the wishlist for a given user. If the circuit breaker is triggered,
        it returns a service unavailable message.
        
        Returns:
            dict: A success message or an error message if the service is unavailable or the item is not found.
        """
        data = request.get_json()
        username = data['customer_username']
        product_id = data['product_id']

        try:
            # Use circuit breaker to fetch the item
            item = circuit_breaker.call(Wishlist.query.filter_by, customer_username=username, product_id=product_id).first()
        except pybreaker.CircuitBreakerError:
            return jsonify({'message': 'Circuit breaker triggered, unable to fetch item from wishlist'}), 503

        if not item:
            return jsonify({'message': 'Item not found in wishlist'}), 404

        try:
            # Use circuit breaker to delete the item
            circuit_breaker.call(db.session.delete, item)
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return jsonify({'message': 'Circuit breaker triggered, unable to delete item from wishlist'}), 503

        return jsonify({'message': 'Item removed from wishlist'}), 200
