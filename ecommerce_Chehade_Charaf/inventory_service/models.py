from database import db
class Goods(db.Model):
    """
    Represents a good item in the inventory system.

    This model defines the structure of the 'goods' table in the database. Each instance of this class 
    represents a single row in the 'goods' table and is used to interact with data related to inventory goods.

    Attributes:
        id (int): The unique identifier of the good.
        name (str): The name of the good item.
        category (str): The category of the good.
        price_per_item (float): The price per unit of the good.
        description (str): A description of the good item.
        stock_count (int): The number of units in stock for the good.
    """
    __tablename__ = 'goods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price_per_item = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    stock_count = db.Column(db.Integer, nullable=False)
    


