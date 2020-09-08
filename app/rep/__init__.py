from flask import Blueprint

bp = Blueprint('rep', __name__)

from app.rep import routes
