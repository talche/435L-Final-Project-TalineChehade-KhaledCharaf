# resources/goods.py

from flask_restful import Resource
from flask import request
from models import Goods
from database import db
from schemas import GoodsSchema

goods_schema = GoodsSchema()
goods_list_schema = GoodsSchema(many=True)

class GoodsListResource(Resource):
    def get(self):
        goods = Goods.query.all()
        result = goods_list_schema.dump(goods)
        return {'goods': result}, 200

    def post(self):
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
        db.session.add(new_goods)
        db.session.commit()
        result = goods_schema.dump(new_goods)
        return {'message': 'Goods added', 'goods': result}, 201

class GoodsResource(Resource):
    def get(self, goods_id):
        goods = Goods.query.get(goods_id)
        if not goods:
            return {'message': 'Goods not found'}, 404
        result = goods_schema.dump(goods)
        return {'goods': result}, 200

    def put(self, goods_id):
        data = request.get_json()
        goods = Goods.query.get(goods_id)
        if not goods:
            return {'message': 'Goods not found'}, 404

        goods.name = data.get('name', goods.name)
        goods.category = data.get('category', goods.category)
        goods.price_per_item = data.get('price_per_item', goods.price_per_item)
        goods.description = data.get('description', goods.description)
        goods.stock_count = data.get('stock_count', goods.stock_count)

        db.session.commit()
        result = goods_schema.dump(goods)
        return {'message': 'Goods updated', 'goods': result}, 200

    def delete(self, goods_id):
        goods = Goods.query.get(goods_id)
        if not goods:
            return {'message': 'Goods not found'}, 404

        db.session.delete(goods)
        db.session.commit()
        return {'message': 'Goods deleted'}, 200
