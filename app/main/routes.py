from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db, oa
from flask_babel import get_locale
from app.main import bp
from app.main.forms import EditProfileForm,EmptyForm, PostForm, DateForm, SearchForm, MessageForm
from app.models import User, Post, Hansard, MajorHeading, Speech, Rep, Paragraph, Message, Notification, Task
import json
import requests
import pandas
from guess_language import guess_language
from app.translate import translate
from datetime import datetime

@bp.before_request
def before_request():
    '''this function runs before any request and is used to generate variables and forms which are universal to any application page'''
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
        g.locale = str(get_locale())
        #The following has been used to enter hansard entries in the database
        # dates = oa.get_debates("senate",year=2020)
        # dates = dates['dates']
        # for date in dates:
        #     if Hansard.query.filter_by(date=date, debate_type = "senate").first():
        #         print(date)
        #     else:
        #         rebuild(date)

######################################ROUTES RELEVANT TO THE HOME PAGE #############################################
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    '''route to the applications homepage'''
    posts = current_user.followed_posts().paginate(1, 5, False) # show the first five comments from the users follow feed.
    return render_template('index.html', title='Home',
                           posts=posts.items)

######################################ROUTES RELEVANT TO NEWSFEED #############################################

@bp.route('/newsfeed', methods=['GET', 'POST'])
@login_required
def newsfeed():
    '''route to show all comments from the users follow feed paginated to have a certain number of entries per page'''
    page = request.args.get('page', 1, type=int) #gets the value of the parameter page, which indicates which page the application is currently in
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False) # A SQLalchemy pagination function which paginates queries in the database into multiple pages with max of POST_PER_PAGE entries per page
    return render_template('explore.html', url= "/newsfeedextra", title = "Your Personal Newsfeed 🗞", posts=posts.items, pages=posts.pages)

@bp.route('/newsfeedextra', methods=['GET', 'POST'])
@login_required
def newsfeedextra():
    '''assistant function to newfeed route usually requested by ajax call to render and send a request including all comments of a query on a specific page number without the navigation bar and pagination'''
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('exploreextra.html', title = "Your Personal Newsfeed 🗞", posts=posts.items, pages=posts.pages)

@bp.route('/search')
@login_required
def search():
    '''allows users to search the database for posts and debate paragraphs that match their interests'''
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, 1,5) #shows the first five comments which match the users query
    paragraphs, total = Paragraph.search(g.search_form.q.data,1,5)  #shows the first five debate paragraphs which match the users query
    return render_template('search.html', title='Search', posts=posts, paragraphs=paragraphs)

######################################ROUTES RELEVANT TO THE EXPLORE PAGE #############################################

@bp.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    '''route to show all comments from the speak up universe paginated to have a certain number of entries per page'''
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False) #query is sorted from newest to oldest post
    return render_template('explore.html', url="/explorextra", title = "Explore 🌎", posts=posts.items, pages=posts.pages) #uses the same html template as explore as they have similar functions

@bp.route('/explorextra', methods=['GET', 'POST'])
@login_required
def exploreextra():
    '''assistant function to explore route usually requested by ajax call to render and send a request including all comments of a query on a specific page number without the navigation bar and pagination'''
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('exploreextra.html', title = "Explore 🌎", posts=posts.items, pages=posts.pages)

######################################ROUTES RELEVANT TO USER PROFILE and USER MESSAGING #############################################

###################################################### USER PROFILES #################################################################

@bp.route('/user/<username>')
@login_required
def user(username):
    '''route to show a user's profile with user details follow and unfollow links, and a preview of their posts'''
    user = User.query.filter_by(username=username).first_or_404() #find query or else raise a 404 error
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(1, 5, False) #paginates and find the newest five comments
    form = EmptyForm()
    return render_template('usertest.html', user=user, posts=posts.items,form=form, username=username)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''route to show a form to users so they can edit their user profile'''
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.postcode = form.postcode.data
        current_user.set_representativeandconst()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET': #shows users their original username, about me and postcode in form
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.postcode.data = current_user.postcode
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

###################################################### USER FOLLOWING REQUESTS #################################################################


@bp.route('/follow/<username>', methods=['GET','POST'])
@login_required
def follow(username):
    '''route to allow users to follow another users post'''
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None: #if there is no such user
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user: #if the user is the current user
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user) #otherwise allow user to follow user
        db.session.commit() #commit changes to database
        flash('You are following {}!'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['GET','POST'])
@login_required
def unfollow(username):
    '''route to allow users to unfollow another users post'''
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None: #if there is no such user
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.index'))
        if user == current_user: #if the user is the current user
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user) #otherwise allow user to unfollow user
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


###################################################### USER POSTS #################################################################


@bp.route('/user/<username>/posts', methods=['GET', 'POST'])
@login_required
def userpost(username):
    '''route to show all comments written by a specific user, paginated to show only a certain number of entries per page, all entries are accessible with an page parameter'''
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('explore.html', url=username+"/postsextra", title = username+"'s posts'📫", posts=posts.items, pages=posts.pages)

@bp.route('/user/<user>/<username>/postsextra', methods=['GET', 'POST'])
@login_required
def userpostextra(username,user):
    '''assistant function to users post route usually requested by ajax call to render and send a request including all comments of a query on a specific page number without the navigation bar and pagination'''
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    return render_template('exploreextra.html', title = username+"'s posts'📫", posts=posts.items, pages=posts.pages)

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    '''route called by the ajax request to translate a users comment into their local language'''
    return jsonify({'text': translate([request.form['text']],
                                      request.form['dest_language'])})



################################################### PRIVATE MESSAGING #################################################################


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    '''allows users to send a message to another user in the speakup universe'''
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title='Send Message',form=form, recipient=recipient)


########################NEEDS TO BE MODIFIED #########################
@bp.route('/messages')
@login_required
def messages():
    '''allows the user to view private messages which have been sent to them'''
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit() #resets the users unseen message count back to zero
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    """allows the browser to use a ajax request to refresh the notification count for a user"""
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


################################################### DEBATE READING #################################################################


@bp.route('/hansard',methods=['GET', 'POST'])
@login_required
def main_hansard():
    """redirects the user to the latest representative parliament debate"""
    obj = Hansard.query.filter_by(debate_type="representatives").order_by(Hansard.date.desc()).first().date
    return redirect(url_for('main.hansard',date=obj))


@bp.route('/hansard/rep/<date>',methods=['GET', 'POST'])
@login_required
def hansard(date):
    """shows the user the representative hansard for a particular date"""
    realdate = date #save real date for later use
    hansard = Hansard.query.filter_by(date=date, debate_type="representatives").first() #finds the hansard in question
    if hansard is None:
        flash('hansard not found.')
        return redirect(url_for('main.index')) #if no hansard is found redirect to the main index with flashed message
    hansards = Hansard.query.filter_by(debate_type="representatives").all() #Queries all the possible representative hansards so it can be rendered as green in the calendar view
    dates = []
    for date in hansards:
        dates.append(str(date.date).replace("-","/"))
    page = request.args.get('page', 1, type=int) #paginates the hansard so it can be viewed with a faster loading time.
    heading = hansard.majorheading.paginate(page, 1, False)
    form1 = PostForm(identifier="FORM1") #creates the form so users can submit new comments
    form2 = DateForm(identifier="FORM2") #creates the form so users can navigate to other hansards through the calender function
    if form1.identifier.data == 'FORM1' and form1.validate_on_submit(): #if the POST request is for new comments add comment to be related to speech they requested and commit to database
        speech = Speech.query.filter_by(exact_id=form1.hidden.data).first()
        post = Post(body=form1.post.data, author=current_user, speech= speech)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.hansard', date=realdate))
    if form2.identifier.data == 'FORM2' and form2.validate_on_submit(): #if the POST request is for navigation to a new hansard, reload with new hansard
        date = form2.date.data.strftime("%Y-%m-%d")
        return redirect(url_for('main.hansard',date=date))
    return render_template('hansard.html',subtitle = "representative debates 🗣", url = "/hansard/rep/"+realdate+"/extra?page=", data = hansard, pages=heading.pages, majorheading = heading.items, dates = dates, form1 = form1, form2=form2)


@bp.route('/hansard/rep/<date>/extra',methods=['GET', 'POST'])
@login_required
def hansardextra(date):
    '''an assistant function to hansard which allows an ajax request to render the hansard viewing page without navigation bar or other details of the full hansard webpage'''
    hansard = Hansard.query.filter_by(date=date, debate_type="representative").first()
    if hansard is None:
        flash('hansard not found.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    heading = hansard.majorheading.paginate(page, 1, False)
    form1 = PostForm(identifier="FORM1")
    return render_template('hansardextra.html',majorheading = heading.items, form1=form1)

@bp.route('/hansardsen',methods=['GET', 'POST'])
@login_required
def main_hansardsen():
    """redirects the user to the latest senate parliament debate"""
    obj = Hansard.query.filter_by(debate_type="senate").order_by(Hansard.date.desc()).first().date
    return redirect(url_for('main.senhansard',date=obj))

@bp.route('/hansard/senate/<date>',methods=['GET', 'POST'])
@login_required
def senhansard(date):
    """shows the user the senate hansard for a particular date for more details please seek the definiton of hansard"""
    realdate = date
    hansard = Hansard.query.filter_by(date=date, debate_type="senate").first()
    hansards = Hansard.query.all()
    dates = []
    page = request.args.get('page', 1, type=int)
    heading = hansard.majorheading.paginate(
        page, 1, False)
    for date in hansards:
        dates.append(str(date.date).replace("-","/"))
    if hansard is None:
        flash('hansard not found.')
        return redirect(url_for('main.index'))
    form1 = PostForm(identifier="FORM1")
    form2 = DateForm(identifier="FORM2")
    if form1.identifier.data == 'FORM1' and form1.validate_on_submit():
        speech = Speech.query.filter_by(exact_id=form1.hidden.data).first()
        language = guess_language(form1.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form1.post.data, author=current_user, speech= speech,
                    language=language)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.senhansard', date=realdate))
    if form2.identifier.data == 'FORM2' and form2.validate_on_submit():
        date = form2.date.data.strftime("%Y-%m-%d")
        return redirect(url_for('main.hansard',date=date))
    return render_template('hansard.html',subtitle = "senate debates 🗣", url = "/hansard/rep/"+realdate+"/extra?page=", data = hansard, pages=heading.pages, majorheading = heading.items, dates = dates, form1 = form1, form2=form2)


@bp.route('/hansard/senate/<date>/extra',methods=['GET', 'POST'])
@login_required
def senhansardextra(date):
    """an assistant function to senhansard, please view hansardextra for a definition of how this function works """
    hansard = Hansard.query.filter_by(date=date, debate_type="senate").first()
    if hansard is None:
        flash('hansard not found.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    heading = hansard.majorheading.paginate(
        page, 1, False)
    form1 = PostForm(identifier="FORM1")
    return render_template('hansardextra.html',majorheading = heading.items, form1=form1)
