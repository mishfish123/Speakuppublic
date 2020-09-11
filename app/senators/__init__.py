from flask import Blueprint

bp = Blueprint('senators', __name__)

from app.senators import routes
