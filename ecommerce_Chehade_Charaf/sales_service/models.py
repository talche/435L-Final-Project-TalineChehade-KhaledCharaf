from database import db

class Goods(db.Model):
    """
    Represents goods/items available in the inventory.

    Attributes:
        id (int): Primary key.
        name (str): Name of the goods.
        category (str): Category of the goods.
        price_per_item (float): Price per single item.
        description (str): Description of the goods.
        stock_count (int): Number of items in stock.
    """
    __tablename__ = 'goods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price_per_item = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    stock_count = db.Column(db.Integer, nullable=False)

class Purchase(db.Model):
    """
    Represents a purchase made by a user.

    Attributes:
        id (int): Primary key.
        username (str): Username of the purchaser.
        goods_id (int): ID of the purchased goods.
        quantity (int): Quantity purchased.
        total_price (float): Total price of the purchase.
        purchase_date (datetime): Date and time of purchase.
    """
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    goods_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)
