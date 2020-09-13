
#this is a blue print for flask to handle the functionalities of the website responsible for representative enquries

from flask import Blueprint

bp = Blueprint('rep', __name__)

from app.rep import routes
