from marshmallow import Schema, fields

class WishlistSchema(Schema):
    id = fields.Int(dump_only=True)
    customer_username = fields.Str(required=True)
    product_id = fields.Int(required=True)
    date_added = fields.DateTime(dump_only=True)

class WishlistAddSchema(Schema):
    customer_username = fields.Str(required=True)
    product_id = fields.Int(required=True)
