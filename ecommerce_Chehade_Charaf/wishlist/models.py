from datetime import datetime
from database import db

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_username = db.Column(db.String(80), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, customer_username, product_id):
        self.customer_username = customer_username
        self.product_id = product_id

    def __repr__(self):
        return f"<Wishlist(customer_username={self.customer_username}, product_id={self.product_id})>"
