from flask import render_template, request
from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    '''handles errors in which no routed page can be found'''
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    '''handles errors in application logic'''
    db.session.rollback()
    return render_template('errors/500.html'), 500
