# app.py

from flask import Flask
from flask_restful import Api
from config import Config
from database import db
from resources.goods import GoodsListResource, GoodsResource

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
api = Api(app)

# Register endpoints
api.add_resource(GoodsListResource, '/goods')
api.add_resource(GoodsResource, '/goods/<int:goods_id>')
with app.app_context():
    db.create_all()  # Create tables based on models
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
