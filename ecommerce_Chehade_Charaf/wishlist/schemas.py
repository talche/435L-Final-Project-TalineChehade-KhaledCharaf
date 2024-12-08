from marshmallow import Schema, fields

class WishlistSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    goods_name = fields.Str(required=True)
    price_per_item = fields.Float(required=True)

