# schemas.py

from marshmallow import Schema, fields, validate, validates_schema


class GoodsSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    category = fields.Str(required=True, validate=validate.OneOf(['food', 'clothes', 'accessories', 'electronics']))
    price_per_item = fields.Float(required=True)
    description = fields.Str()
    stock_count = fields.Int(required=True, validate=validate.Range(min=0))

    @validates_schema
    def validate_price(self, data, **kwargs):
        if data['price_per_item'] <= 0:
            raise ValidationError('Price per item must be greater than 0.', 'price_per_item')

    @validates_schema
    def validate_stock_count(self, data, **kwargs):
        if data['stock_count'] < 0:
            raise ValidationError('Stock count cannot be negative.', 'stock_count')