import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
if not os.getenv('DOCKER_CONTAINER'):
    load_dotenv(os.path.join(basedir, os.getenv('ENV_FILE', '.env.local')))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '0')
    FLASK_PORT = os.getenv('FLASK_PORT', '8080')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')