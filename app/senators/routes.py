from flask import render_template, flash, redirect, url_for, request,jsonify,current_app
from werkzeug.urls import url_parse
from app import db, oa
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Post, Hansard, MajorHeading, Speech, Rep, Senate
import requests
from app.senators import bp
import json
from app.main.forms import SearchForm
import pandas
from guess_language import guess_language
from app.translate import translate

@bp.route('/allsenators',methods=['GET', 'POST'])
@login_required
def allsenators():
    '''route shows all the senators in parliament right now in a card format and with pagination'''
    page = request.args.get('page', 1, type=int)
    reps = Senate.query.paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('allsenators.html', reps=reps.items, pages=reps.pages)

@bp.route('/allsenatorsextra',methods=['GET', 'POST'])
@login_required
def allsenatorsextra():
    '''An assistant function of all senators which allows the browser to request a ajax query just for the card contents and not the entire website'''
    page = request.args.get('page', 1, type=int)
    reps = Senate.query.paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('allrepsnew.html', reps=reps.items,type=type, pages=reps.pages)


@bp.route('/mystatesenators')
@login_required
def mystatesenators():
    '''shows all the senators from the user's state'''
    postcode = current_user.openaustraliadata()
    response = requests.get('http://v0.postcodeapi.com.au/suburbs/'+postcode+'.json') #converts a postcode to their regional information
    json_data = json.loads(response.text)
    state = json_data[0]['state']['abbreviation'] #get the state the user is from.
    oa_data = oa.get_senators(state=state) #request data from senator
    return render_template('nature.html',data = oa_data)


@bp.route('/senator/<person_id>',methods=['GET', 'POST'])
@login_required
def personid(person_id):
    '''shows a senator's personal profile based on their OA personal id'''
    response = requests.get('https://theyvoteforyou.org.au/api/v1/people/'+str(person_id)+'.json?key=k4Pwf%2BFaW2ygOTWEOCVn') #gets data from they vote for you API
    json_data = json.loads(response.text)
    image = "https://www.openaustralia.org.au/images/mpsL/"+str(json_data['id'])+".jpg" #gets portrait of the senator from OA
    oa_data = oa.get_senator(person_id)[0] #gets data about a senator from OA
    value = oa.get_senator(person_id)[0]['full_name'].split()
    df = pandas.read_csv('app/senators/senator.csv', engine='python') #gets data about a senator from a personal database stored in a file locally.
    result = df.loc[(df['Surname'] == value[-1]) & (df['First Name'] == value[0])]
    if result.empty:
        result = df.loc[(df['Surname'] == value[-1]) & (df['Preferred Name'] == value[0])]
    return render_template('senator.html', data = json_data, image = image, oa = oa_data, excel = result, type = type)
