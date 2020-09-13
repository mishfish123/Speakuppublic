#this is a blue print for flask to handle the functionalities of the website responsible for senate enquries

from flask import Blueprint

bp = Blueprint('senators', __name__)

from app.senators import routes
