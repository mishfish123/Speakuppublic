from datetime import datetime
from hashlib import md5
from app import db, login, oa
from flask_login import UserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt
from app import db, login
from app.search import add_to_index, remove_from_index, query_index
import json
import redis
import rq


class SearchableMixin(object):
    """a sub database class which has been modified such that when a searchable object is created, the object is also saved in the elasticsearch database"""
    @classmethod
    def search(cls, expression, page, per_page): #cls is the model class in question
        """invoke a search in the elasticsearch database and converts the recieved indices into a SQLalchemy object"""
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i)) #maintains order from elasticsearch search
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total #filters database queries to only select the indices included in search results
            #order by preserves the database order elastic search had returned with

    @classmethod
    def before_commit(cls, session):
        "records all the objects that are being added to the commit"
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        """records all the committed changes to elasticsearch"""
        for obj in session._changes['add']: #fetches _changes object from before_commit function and adds it to the index.
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        """adds database objects into elasticsearch"""
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit) #attaches before and after commit methods to the corresponding events
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
) #produces a index table with foreign keys that keep track of the relationship between user followers and followed users.

class User(UserMixin, db.Model): #User Mixin is a Flask-Login sub class which adds functionality the login requires for the user model
    """Model representation of users in the website"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    representative = db.Column(db.String(100))
    constituency = db.Column(db.String(100))
    postcode = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')

    def __repr__(self):
        """represents a user object"""
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """sets the password of a user and stores in a hash table"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """checks a users password to that of the hashtable"""
        return check_password_hash(self.password_hash, password)

    def set_representativeandconst(self):
        """sets a users representative and constituency"""
        self.representative = oa.get_representatives(int(self.postcode))[0]['full_name']
        self.constituency = oa.get_representatives(self.postcode)[0]['constituency']
        self.personid = oa.get_representatives(self.postcode)[0]['person_id']

    def openaustraliadata(self):
        """returns the postcode for a user"""
        return self.postcode

    def avatar(self, size):
        """returns a avatar for a user"""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        """allows the current user to follow another user"""
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """allows the current user to unfollow another user"""
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """indicates whether one user is following another user"""
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """shows the posts of a users follow feed"""
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id) #joins the posts with the same user.id and followed id
        own = Post.query.filter_by(user_id=self.id) #create query which takes the users own posts
        return followed.union(own).order_by(Post.timestamp.desc()) #joins both queries above together to generate the users newsfeed

    def get_reset_password_token(self, expires_in=600):
        """generates token required for user to reset password"""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod #static method means it can be invoked without passing a member of a class to it
    def verify_reset_password_token(token):
        """verifies token required for user to reset password"""
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def new_messages(self):
        """shows how many new messages has gotten since checking the messaging page"""
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        """add notifications"""
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model,SearchableMixin): #SearchableMixin included to allow paragraphs to be written to elasticsearch
    "Model to represent user comments"
    __searchable__ = ['body']  #indicates the body property must be added to elasticasearch database
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    speech_id = db.Column(db.Integer, db.ForeignKey('speech.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Hansard(db.Model):
    "Model to map Parliametry Hansards by date and debate type (senate or rep)"
    __bind_key__ = 'hansard' #writes data into SQLfile instead of Azure SQL database for faster retrieval of data.
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(140))
    debate_type = db.Column(db.String(140))
    majorheading = db.relationship('MajorHeading', backref='hansard', lazy='dynamic')

    def __repr__(self):
        return '<Hansard {}>'.format(self.date)

class MajorHeading(db.Model):
    "Model to map Major headings to Parliametry Hansards"
    __tablename__ = 'majorheading'
    __bind_key__ = 'hansard' #writes data into SQLfile instead of Azure SQL database for faster retrieval of data.
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,index=True)
    hansard_id = db.Column(db.Integer, db.ForeignKey('hansard.id'))
    body = db.Column(db.String(1000))
    minorheading = db.relationship('MinorHeading', backref='majorheading', lazy='dynamic')

    def __repr__(self):
        return '<MajorHeading {} {}>'.format(self.body, self.order_id)

class MinorHeading(db.Model):
    "Model to map Minor heading to Major headings of a parliametry Hansard"
    __tablename__ = 'minorheading'
    __bind_key__ = 'hansard' #writes data into SQLfile instead of Azure SQL database for faster retrieval of data.
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,index=True)
    major_id = db.Column(db.Integer, db.ForeignKey('majorheading.id'))
    body = db.Column(db.String())
    speech = db.relationship('Speech', backref='minorheading', lazy='dynamic')


    def __repr__(self):
        return '<MinorHeading {} {}>'.format(self.body, self.order_id)

class Speech(db.Model):
    "Model to map Speeches to a Minor heading of Major headings of a parliametry Hansard"
    __tablename__ = 'speech'
    __bind_key__ = 'hansard' #writes data into SQLfile instead of Azure SQL database for faster retrieval of data.
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer,index=True)
    minor_id = db.Column(db.Integer, db.ForeignKey('minorheading.id'))
    exact_id = db.Column(db.String(140))
    author_id = db.Column(db.String(140))
    paragraph = db.relationship('Paragraph', backref='speech', lazy='dynamic')
    post = db.relationship('Post', backref='speech', lazy='dynamic')


    def __repr__(self):
        return '<Speech {} {}>'.format(self.author_id, self.order_id)

class Paragraph(db.Model, SearchableMixin): #SearchableMixin included to allow paragraphs to be written to elasticsearch
    "Model to map paragraphs to speech of a Minor heading of Major headings of a parliametry Hansard"
    __bind_key__ = 'hansard' #writes data into SQLfile instead of Azure SQL database for faster retrieval of data.
    __tablename__ = 'paragraph'
    __searchable__ = ['body'] #indicates the body property must be added to elasticasearch database
    id = db.Column(db.Integer, primary_key=True)
    speech_id = db.Column(db.Integer, db.ForeignKey('speech.id'))
    body= db.Column(db.String())

    def __repr__(self):
        return '<Paragraph {}>'.format(self.body)


class Rep(db.Model):
    """Model to representative of the parliament from a file database stored in rep/rep.csv"""
    __bind_key__ = 'hansard'#writes data into SQLfile instead of Azure SQL database for faster retrieval of data.
    id = db.Column(db.Integer, primary_key=True)
    Honorific = db.Column(db.String(140))
    Salutation = db.Column(db.String(140))
    PostNomination = db.Column(db.String(140))
    Surname = db.Column(db.String(140))
    Image = db.Column(db.String(140))
    FirstName = db.Column(db.String(140))
    PreferredName = db.Column(db.String(140))
    Email = db.Column(db.String(140))
    Facebook = db.Column(db.String(140))
    Twitter = db.Column(db.String(140))
    Other = db.Column(db.String(140))
    Telephone = db.Column(db.String(140))
    ElectorateAddress = db.Column(db.String(140))
    ElectoratePhone = db.Column(db.String(140))
    ElectoratePostal = db.Column(db.String(140))
    ElectorateSuburb = db.Column(db.String(140))
    Titles = db.Column(db.String(140))
    Postcode = db.Column(db.String(140))

class Senate(db.Model):
    """Model to senator of the parliament from a file database stored in senators/senators.csv"""
    __bind_key__ = 'hansard' #writes data into SQLfile instead of Azure SQL database for faster retrieval of data.
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    Image = db.Column(db.String(140))
    Surname = db.Column(db.String(140))
    FirstName = db.Column(db.String(140))
    PreferredName = db.Column(db.String(140))
    Email = db.Column(db.String(140))
    Facebook = db.Column(db.String(140))
    Twitter = db.Column(db.String(140))
    Other = db.Column(db.String(140))
    ElectorateAddress = db.Column(db.String(140))
    ElectoratePhone = db.Column(db.String(140))
    ElectoratePostal = db.Column(db.String(140))
    ElectorateSuburb = db.Column(db.String(140))
    Titles = db.Column(db.String(140))
    Postcode = db.Column(db.String(140))

class Message(db.Model):
    "Representation of private messages sent between users"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    "Representation for user notifications"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))
