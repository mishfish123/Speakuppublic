from flask import render_template, flash, redirect, url_for, request,jsonify,current_app
from werkzeug.urls import url_parse
from app import db, oa
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Post, Hansard, MajorHeading, Speech, Rep
import requests
from app.rep import bp
import json
import pandas
from guess_language import guess_language
from app.translate import translate


@bp.route('/allrepresentatives',methods=['GET', 'POST'])
@login_required
def allrepresentatives():
    page = request.args.get('page', 1, type=int)
    reps = Rep.query.paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('rep.allrepresentatives', page=reps.next_num) \
        if reps.has_next else None
    prev_url = url_for('rep.allrepresentatives', page=reps.prev_num) \
        if reps.has_prev else None
    return render_template('allrep.html', reps=reps.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/myrepresentative')
@login_required
def myrepresentative():
    postcode = current_user.openaustraliadata()
    return redirect(url_for("rep.postcode",postcode = postcode))


@bp.route('/representative/<postcode>',methods=['GET', 'POST'])
@login_required
def postcode(postcode):
    if len(oa.get_representatives(postcode)) > 1:
        people = []
        for representative in oa.get_representatives(postcode):
            person = Rep.query.filter_by(FirstName=representative['first_name'], Surname=representative['last_name']).first()
            if person == []:
                person = Rep.query.filter_by(PreferredName=representative['first_name'], Surname=representative['last_name']).first()
            people.append(person)
        return render_template('test.html', reps=people, postcode=postcode)
    else:
        oa_data = oa.get_representatives(postcode)[0]
        person_id = oa_data['person_id']
        return redirect(url_for("rep.personid",person_id = person_id))

@bp.route('/rep/<person_id>',methods=['GET', 'POST'])
@login_required
def personid(person_id):
    response = requests.get('https://theyvoteforyou.org.au/api/v1/people/'+str(person_id)+'.json?key=k4Pwf%2BFaW2ygOTWEOCVn')
    json_data = json.loads(response.text)
    image = "https://www.openaustralia.org.au/images/mpsL/"+str(json_data['id'])+".jpg"
    oa_data = oa.get_representative(person_id)[0]
    value = oa.get_representative(person_id)[0]['full_name'].split()
    df = pandas.read_csv('app/rep/Rep.csv', engine='python')
    result = df.loc[(df['Surname'] == value[-1]) & (df['First Name'] == value[0])]
    if result.empty:
        result = df.loc[(df['Surname'] == value[-1]) & (df['Preferred Name'] == value[0])]
    return render_template('rep.html', data = json_data, image = image, oa = oa_data, excel = result, type = type)
