from database import db

class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)  # Associate wishlist with the username
    goods_name = db.Column(db.String(255), nullable=False)  # Store the name of the product
    price_per_item = db.Column(db.Float, nullable=False)


