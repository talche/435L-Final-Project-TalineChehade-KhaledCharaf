# models.py

from database import db
from datetime import datetime

class Review(db.Model):
    """
    Model representing a product review.

    Attributes:
        id (int): Primary key.
        product_id (int): ID of the product being reviewed.
        username (str): Username of the reviewer.
        rating (int): Rating given by the user (1-5).
        comment (str): Review comment.
        created_at (datetime): Timestamp when the review was created.
        updated_at (datetime): Timestamp when the review was last updated.
        is_approved (bool): Approval status of the review.
    """

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
