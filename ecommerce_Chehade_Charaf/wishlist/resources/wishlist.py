from flask_restful import Resource
from flask import request
from models import Wishlist
from schemas import WishlistSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
import pybreaker

# Create the circuit breaker object for wishlist service
breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)

wishlist_schema = WishlistSchema()

class WishlistResource(Resource):
    """
    Resource for handling wishlist operations: adding, viewing, and deleting products.
    This does not directly query the Goods model but assumes goods_name is the identifier.
    """

    @jwt_required()
    def post(self):
        """
        Add a product to the user's wishlist using the goods_name and price_per_item.

        Expects JSON data with 'goods_name' and 'price_per_item'.

        Returns:
            tuple: A tuple containing a JSON response and HTTP status code.
        """
        data = request.get_json()

        # Validate if goods_name and price_per_item are provided
        if 'goods_name' not in data or 'price_per_item' not in data:
            return {'message': 'goods_name and price_per_item are required'}, 400

        goods_name = data['goods_name']
        price_per_item = data['price_per_item']
        username = get_jwt_identity()  # Get the authenticated user's username

        # Check if the product is already in the wishlist for the user
        existing_wishlist_item = Wishlist.query.filter_by(username=username, goods_name=goods_name).first()
        if existing_wishlist_item:
            return {'message': 'Product already in wishlist'}, 400

        # Add the product to the wishlist (Note: no need for goods_id)
        new_wishlist_item = Wishlist(username=username, goods_name=goods_name, price_per_item=price_per_item)
        db.session.add(new_wishlist_item)
        db.session.commit()

        result = wishlist_schema.dump(new_wishlist_item)
        return {'message': 'Product added to wishlist', 'wishlist_item': result}, 201

    @jwt_required()
    def get(self):
        """
        Get the products in the user's wishlist.

        Returns:
            tuple: A tuple containing a JSON response and HTTP status code.
        """
        username = get_jwt_identity()  # Get the authenticated user's username

        try:
            # Fetch all wishlist items for the authenticated user
            wishlist_items = breaker.call(lambda: Wishlist.query.filter_by(username=username).all())
        except pybreaker.CircuitBreakerError:
            return {'message': 'Service unavailable, please try again later'}, 503

        if not wishlist_items:
            return {'message': 'Wishlist is empty'}, 200

        result = wishlist_schema.dump(wishlist_items)
        return {'wishlist': result}, 200

    @jwt_required()
    def delete(self):
        """
        Delete a product from the user's wishlist by goods name.

        Expects JSON data with 'goods_name' to remove a specific item.

        Returns:
            tuple: A tuple containing a JSON response and HTTP status code.
        """
        data = request.get_json()
        if 'goods_name' not in data:
            return {'message': 'goods_name is required'}, 400

        goods_name = data['goods_name']
        username = get_jwt_identity()  # Get the authenticated user's username

        try:
            # Fetch the wishlist item for the user and goods name
            wishlist_item = breaker.call(lambda: Wishlist.query.filter_by(username=username, goods_name=goods_name).first())
        except pybreaker.CircuitBreakerError:
            return {'message': 'Service unavailable, please try again later'}, 503

        if not wishlist_item:
            return {'message': 'Product not found in wishlist'}, 404

        # Delete the item from the wishlist
        db.session.delete(wishlist_item)
        db.session.commit()

        return {'message': 'Product removed from wishlist'}, 200
