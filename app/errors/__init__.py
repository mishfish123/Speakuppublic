#this is a blue print for flask to handle routing errors

from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers
