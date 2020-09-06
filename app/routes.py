from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db, oa
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    EmptyForm, PostForm, DateForm
from app.models import User, Post, Hansard, MajorHeading, Speech
import requests
import json
import requests
from io import BytesIO
from pprint import pprint
from lxml.etree import iterparse
from collections import OrderedDict
import pandas
import math





@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, 3, False)
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, postcode=form.postcode.data)
        user.set_password(form.password.data)
        user.set_representativeandconst()
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, 3, False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('usertest.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.postcode = form.postcode.data
        current_user.set_representativeandconst()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.postcode.data = current_user.postcode
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/follow/<username>', methods=['GET','POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['GET','POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('explore.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)



@app.route('/myrepresentative')
@login_required
def myrepresentative():
    postcode = current_user.openaustraliadata()
    return redirect(url_for("representative",postcode = postcode))


@app.route('/representative/<postcode>',methods=['GET', 'POST'])
@login_required
def representative(postcode):
    oa_data = oa.get_representatives(postcode)[0]
    person_id = oa_data['person_id']
    response = requests.get('https://theyvoteforyou.org.au/api/v1/people/'+str(person_id)+'.json?key=k4Pwf%2BFaW2ygOTWEOCVn')
    json_data = json.loads(response.text)
    image = "https://www.openaustralia.org.au/images/mpsL/"+str(json_data['id'])+".jpg"
    value = oa.get_representatives(postcode)[0]['full_name'].split()
    df = pandas.read_csv('app/Rep.csv', engine='python')
    result = df.loc[(df['Surname'] == value[-1]) & (df['First Name'] == value[0])]
    if result.empty:
        result = df.loc[(df['Surname'] == value[-1]) & (df['Preferred Name'] == value[0])]
    return render_template('rep.html', data = json_data, image = image, oa = oa_data, excel = result, type = type)


@app.route('/hansard',methods=['GET', 'POST'])
@login_required
def main():
    obj = Hansard.query.order_by(Hansard.date.desc()).first().date
    return redirect(url_for('hansard',date=obj))


@app.route('/hansard/<date>',methods=['GET', 'POST'])
@login_required
def hansard(date):
    hansard = Hansard.query.filter_by(date=date).first()
    hansards = Hansard.query.all()
    dates = []
    for date in hansards:
        dates.append(str(date.date).replace("-","/"))
    if hansard is None:
        flash('hansard not found.')
        return redirect(url_for('index'))
    form1 = PostForm(identifier="FORM1")
    form2 = DateForm(identifier="FORM2")
    if form1.identifier.data == 'FORM1' and form1.validate_on_submit():
        speech = Speech.query.filter_by(exact_id=form1.hidden.data).first()
        post = Post(body=form1.post.data, author=current_user, speech= speech)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    if form2.identifier.data == 'FORM2' and form2.validate_on_submit():
        date = form2.date.data.strftime("%Y-%m-%d")
        return redirect(url_for('hansard',date=date))
    return render_template('hansard.html',data = hansard, dates = dates, form1 = form1, form2=form2)

@app.route('/calendar',methods=['GET', 'POST'])
@login_required
def calendar():
    return render_template('calendar.html')
