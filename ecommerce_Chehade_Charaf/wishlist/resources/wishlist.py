from flask_restful import Resource
from flask import request
from database import db
from models import Wishlist
from sqlalchemy.exc import SQLAlchemyError

class WishlistResource(Resource):
    """
    Resource for handling wishlist operations: adding, viewing, and deleting products.
    """
    
    def post(self):
        """
        Add a product to the user's wishlist.
        
        Expects JSON data with 'username', 'goods_name', and 'price_per_item'.
        
        Returns:
            tuple: A tuple containing a JSON response and HTTP status code.
        """
        data = request.get_json()

        # Validate if required fields are provided
        if not all(key in data for key in ('username', 'goods_name', 'price_per_item')):
            return {'message': 'username, goods_name, and price_per_item are required'}, 400

        username = data['username']
        goods_name = data['goods_name']
        price_per_item = data['price_per_item']

        # Check if the product is already in the wishlist for the user
        existing_wishlist_item = Wishlist.query.filter_by(username=username, goods_name=goods_name).first()
        if existing_wishlist_item:
            return {'message': 'Product already in wishlist'}, 400

        # Add the product to the wishlist
        new_wishlist_item = Wishlist(username=username, goods_name=goods_name, price_per_item=price_per_item)

        try:
            db.session.add(new_wishlist_item)
            db.session.commit()
            return {'message': 'Product added to wishlist', 'wishlist_item': {
                'id': new_wishlist_item.id,
                'username': new_wishlist_item.username,
                'goods_name': new_wishlist_item.goods_name,
                'price_per_item': new_wishlist_item.price_per_item
            }}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    def get(self):
        """
        Get all products in the user's wishlist.
        
        Expects query parameter 'username'.
        
        Returns:
            tuple: A tuple containing a JSON response and HTTP status code.
        """
        username = request.args.get('username')

        if not username:
            return {'message': 'username is required'}, 400

        # Fetch all wishlist items for the user
        wishlist_items = Wishlist.query.filter_by(username=username).all()

        if not wishlist_items:
            return {'message': 'Wishlist is empty'}, 200

        result = [{'id': item.id, 'username': item.username, 'goods_name': item.goods_name, 'price_per_item': item.price_per_item} for item in wishlist_items]

        return {'wishlist': result}, 200

    def delete(self):
        """
        Delete a product from the user's wishlist by goods name.
        
        Expects JSON data with 'username' and 'goods_name'.
        
        Returns:
            tuple: A tuple containing a JSON response and HTTP status code.
        """
        data = request.get_json()

        if 'username' not in data or 'goods_name' not in data:
            return {'message': 'username and goods_name are required'}, 400

        username = data['username']
        goods_name = data['goods_name']

        # Fetch the wishlist item for the user and goods name
        wishlist_item = Wishlist.query.filter_by(username=username, goods_name=goods_name).first()

        if not wishlist_item:
            return {'message': 'Product not found in wishlist'}, 404

        try:
            # Delete the item from the wishlist
            db.session.delete(wishlist_item)
            db.session.commit()
            return {'message': 'Product removed from wishlist'}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': str(e)}, 500
