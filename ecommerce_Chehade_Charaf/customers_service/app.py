from flask import Flask, current_app
from flask_restful import Api
from flask_jwt_extended import JWTManager
from config import Config
from database import db
from resources.customer import CustomerRegister, CustomerResource, CustomerList, DeductBalance, AddBalance
import os
#from dotenv import load_dotenv
from werkzeug.middleware.profiler import ProfilerMiddleware


def create_app(config_object=Config):
    """
    Create and configure the Flask application.

    Args:
        config_object (object): Configuration object for Flask.

    Returns:
        Flask: Configured Flask application instance.
    """
    # Initialize Flask app
    #load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    api = Api(app)
    
    api.add_resource(CustomerRegister, '/customers/register')
    api.add_resource(CustomerResource, '/customers/<string:username>')
    api.add_resource(CustomerList, '/customers')
    api.add_resource(DeductBalance, '/customers/deduct-balance')
    api.add_resource(AddBalance, '/customers/add-balance')

    # Add ProfilerMiddleware only if FLASK_ENV is development
    print("FLASK_ENV:", os.getenv("FLASK_ENV"))
    if os.getenv('FLASK_ENV') == 'development':
        print("in the if hii")
        profile_dir = '/performance_profiler'
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            restrictions=[30],  # Show top 30 functions
            profile_dir=profile_dir
        )
        app.logger.info("ProfilerMiddleware enabled. Profiling data will be saved to /performance_profiler.")

    # Load environment variables from .env
    #load_dotenv()
    print("SQLALCHEMY_DATABASE_URI:", os.getenv("SQLALCHEMY_DATABASE_URI"))
    print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001)
