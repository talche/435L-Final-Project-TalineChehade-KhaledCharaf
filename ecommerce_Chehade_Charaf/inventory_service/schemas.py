# schemas.py

from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class GoodsSchema(Schema):
    """
    Schema for serializing and validating goods data.

    This schema validates and serializes data for goods, including fields such as name, category,
    price, description, and stock count. It ensures the data meets the required constraints before
    being processed or persisted.

    Attributes:
        id (int): Unique identifier for the goods item (auto-generated).
        name (str): The name of the goods item.
        category (str): The category of the goods item. 
        price_per_item (float): The price of a single item.
        description (str): An optional description of the goods item.
        stock_count (int): The number of items available in stock.

    Methods:
        validate_price(data): Ensures that the price per item is greater than 0.
        validate_stock_count(data): Ensures that the stock count is not negative.
    """
    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    category = fields.Str(required=True, validate=validate.OneOf(['food', 'clothes', 'accessories', 'electronics']))
    price_per_item = fields.Float(required=True)
    description = fields.Str()
    stock_count = fields.Int(required=True, validate=validate.Range(min=0))

    @validates_schema
    def validate_price(self, data, **kwargs):
        """
        Validates that the price per item is greater than 0.
        """
        if data['price_per_item'] <= 0:
            raise ValidationError('Price per item must be greater than 0.', 'price_per_item')

    @validates_schema
    def validate_stock_count(self, data, **kwargs):
        """
        Validates that the stock count is not negative.
        """
        if data['stock_count'] < 0:
            raise ValidationError('Stock count cannot be negative.', 'stock_count')
