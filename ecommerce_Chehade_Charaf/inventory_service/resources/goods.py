import pybreaker
from flask_restful import Resource
from flask import request
from models import Goods
from database import db
from schemas import GoodsSchema
import logging

# Initialize the circuit breaker
circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)  # Max 3 failures, reset after 60 seconds

goods_schema = GoodsSchema()
goods_list_schema = GoodsSchema(many=True)

class GoodsListResource(Resource):
    """
    Resource for managing the list of goods.

    Supports GET and POST operations for retrieving all goods or adding new goods.
    """
    
    def get(self):
        """
        Handle GET request to retrieve all goods.

        This method retrieves all goods from the database. If the circuit breaker is triggered,
        it returns a message indicating that the service is unavailable.

        Returns:
            dict: A list of all goods or an error message if the service is unavailable.
        """
        try:
            goods = circuit_breaker.call(Goods.query.all)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch goods'}, 503

        result = goods_list_schema.dump(goods)
        return {'goods': result}, 200

    def post(self):
        """
        Handle POST request to add new goods.

        This method validates the input data, checks for errors, and adds the new goods to the database.
        If the circuit breaker is triggered, it returns a service unavailable message.

        Returns:
            dict: A success message with the added goods details or an error message if validation fails.
        """
        data = request.get_json()
        errors = goods_schema.validate(data)
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, 400

        new_goods = Goods(
            name=data['name'],
            category=data['category'],
            price_per_item=data['price_per_item'],
            description=data.get('description', ''),
            stock_count=data['stock_count']
        )
        
        try:
            circuit_breaker.call(db.session.add, new_goods)
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to add goods'}, 503

        result = goods_schema.dump(new_goods)
        return {'message': 'Goods added', 'goods': result}, 201

class GoodsResource(Resource):
    """
    Resource for managing individual goods.

    Supports GET, PUT, and DELETE operations for retrieving, updating, and deleting goods by ID.
    """
    
    def get(self, goods_id):
        """
        Handle GET request to retrieve a specific good by its ID.

        This method fetches a specific good from the database. If the circuit breaker is triggered,
        it returns a message indicating that the service is unavailable.

        Args:
            goods_id (int): The ID of the good to retrieve.

        Returns:
            dict: The goods data or an error message if the service is unavailable or the good is not found.
        """
        try:
            goods = circuit_breaker.call(Goods.query.get, goods_id)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch good'}, 503

        if not goods:
            return {'message': 'Goods not found'}, 404
        result = goods_schema.dump(goods)
        return {'goods': result}, 200

    def put(self, goods_id):
        """
        Handle PUT request to update a specific good by its ID.

        This method updates an existing good's information such as name, price, stock, etc. It will 
        return an error message if the good is not found or if the circuit breaker is triggered.

        Args:
            goods_id (int): The ID of the good to update.

        Returns:
            dict: The updated goods data or an error message.
        """
        data = request.get_json()
        try:
            goods = circuit_breaker.call(Goods.query.get, goods_id)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch good'}, 503

        if not goods:
            return {'message': 'Goods not found'}, 404

        goods.name = data.get('name', goods.name)
        goods.category = data.get('category', goods.category)
        goods.price_per_item = data.get('price_per_item', goods.price_per_item)
        goods.description = data.get('description', goods.description)
        goods.stock_count = data.get('stock_count', goods.stock_count)

        try:
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to update good'}, 503

        result = goods_schema.dump(goods)
        return {'message': 'Goods updated', 'goods': result}, 200

    def delete(self, goods_id):
        """
        Handle DELETE request to remove a specific good by its ID.

        This method deletes the specified good from the database. If the good is not found or if the
        circuit breaker is triggered, it returns an appropriate error message.

        Args:
            goods_id (int): The ID of the good to delete.

        Returns:
            dict: A success message or an error message if the service is unavailable or the good is not found.
        """
        try:
            goods = circuit_breaker.call(Goods.query.get, goods_id)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to fetch good'}, 503

        if not goods:
            return {'message': 'Goods not found'}, 404

        try:
            circuit_breaker.call(db.session.delete, goods)
            circuit_breaker.call(db.session.commit)
        except pybreaker.CircuitBreakerError:
            return {'message': 'Circuit breaker triggered, unable to delete good'}, 503

        return {'message': 'Goods deleted'}, 200
