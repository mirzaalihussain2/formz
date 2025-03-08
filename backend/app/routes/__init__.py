from flask import Blueprint

bp = Blueprint('routes', __name__)

from app.routes import hello, website_to_video