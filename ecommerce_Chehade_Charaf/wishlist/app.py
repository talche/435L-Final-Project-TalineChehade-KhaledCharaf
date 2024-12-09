from flask import Flask
from flask_restful import Api
from resources.wishlist import WishlistResource  # Assuming your WishlistResource class is in wishlist.py
from database import db
from config import Config  # Your config file with DB settings

# Initialize the Flask app
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Create the API instance
api = Api(app)

# Add the Wishlist API resource
api.add_resource(WishlistResource, '/wishlist', '/wishlist/<string:customer_username>')

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port= 5005)
