# schemas.py

from marshmallow import Schema, fields, validate

class GoodsSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    price_per_item = fields.Float(required=True)
    description = fields.Str()
    stock_count = fields.Int(required=True)

class PurchaseSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    goods_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    total_price = fields.Float(dump_only=True)
    purchase_date = fields.DateTime(dump_only=True)
