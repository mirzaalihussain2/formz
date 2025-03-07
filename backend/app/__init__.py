from flask import Flask
from flask_cors import CORS
from config import Config
import logging

# Removes "ERROR:root:" from the start of each error log
logging.basicConfig(
    format='%(message)s',
    level=logging.INFO
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Running CORS in prod, as well as local
    CORS(app, resources={
        r"/*": {
            "origins": app.config['FRONTEND_URL'],
            "methods": ["GET", "POST"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Register blueprints
    from app.routes import bp as bp
    app.register_blueprint(bp, url_prefix='/')
    
    return app