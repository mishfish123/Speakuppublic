#this is a blue print for flask handle the main functionalities of the website

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
