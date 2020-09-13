#this is a blue print for flask to handle authentication

from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes
#import is down below to prevent secular dependencies
