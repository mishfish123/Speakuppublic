from flask import render_template, flash, redirect, url_for, request,jsonify,current_app
from werkzeug.urls import url_parse
from app import db, oa
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Post, Hansard, MajorHeading, Speech, Rep, Senate
import requests
from app.rep import bp
import json
from app.main.forms import SearchForm
import pandas
from guess_language import guess_language
from app.translate import translate


@bp.route('/allrepresentatives',methods=['GET', 'POST'])
@login_required
def allrepresentatives():
    '''route shows all the representatives in parliament right now'''
    page = request.args.get('page', 1, type=int)
    reps = Rep.query.paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('allrep.html', reps=reps.items, type=type, pages=reps.pages)


@bp.route('/allrepresentativesextra',methods=['GET', 'POST'])
@login_required
def allrepresentativesextra():
    '''assistant function to allrepresentatives , allows pagination to occur as a ajax request within a webpage'''
    page = request.args.get('page', 1, type=int)
    reps = Rep.query.paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('allrepsextra.html', reps=reps.items,type=type, pages=reps.pages) #renders a webpage which doesnt have navbar elements.


@bp.route('/myrepresentative')
@login_required
def myrepresentative():
    '''redirects users to a page which shows who their parliamentary members are'''
    postcode = current_user.openaustraliadata() #find users postcode
    return redirect(url_for("rep.postcode",postcode = postcode)) #redirect user to postcode


@bp.route('/representative/<postcode>',methods=['GET', 'POST'])
@login_required
def postcode(postcode):
    '''shows users who their current representatives in parliament are in a card format'''
    if len(oa.get_representatives(postcode)) > 1: #if there is more than one representative for a postcode:
        people = []
        for representative in oa.get_representatives(postcode): #search representative in database based on first name and last name.
            person = Rep.query.filter_by(FirstName=representative['first_name'], Surname=representative['last_name']).first()
            if person == []: #if this search does not work, try to use the representatives preferred name.
                person = Rep.query.filter_by(PreferredName=representative['first_name'], Surname=representative['last_name']).first() #iif
            people.append(person)
        return render_template('repbypostcode.html', reps=people, postcode=postcode) #show representatives in a card format.
    else:
        oa_data = oa.get_representatives(postcode)[0] #if there is only one representative, redirect to representatives personal profile
        person_id = oa_data['person_id']
        return redirect(url_for("rep.personid",person_id = person_id))

@bp.route('/rep/<person_id>',methods=['GET', 'POST'])
@login_required
def personid(person_id):
    '''shows a representatives personal profile based on their OA personal id'''
    response = requests.get('https://theyvoteforyou.org.au/api/v1/people/'+str(person_id)+'.json?key=k4Pwf%2BFaW2ygOTWEOCVn') #get person's details from they vote for you API
    json_data = json.loads(response.text)
    image = "https://www.openaustralia.org.au/images/mpsL/"+str(json_data['id'])+".jpg" #get the parliament memebers portrait from open australia
    oa_data = oa.get_representative(person_id)[0] #obtain the persons information from open australia
    value = oa.get_representative(person_id)[0]['full_name'].split()
    df = pandas.read_csv('app/rep/Rep.csv', engine='python') #get the persons contact information from file Rep.csv which has additional details about the member
    result = df.loc[(df['Surname'] == value[-1]) & (df['First Name'] == value[0])]
    if result.empty:
        result = df.loc[(df['Surname'] == value[-1]) & (df['Preferred Name'] == value[0])]
    return render_template('rep.html', data = json_data, image = image, oa = oa_data, excel = result, type = type)
