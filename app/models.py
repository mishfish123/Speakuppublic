from datetime import datetime
from hashlib import md5
from app import db, login, oa
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
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

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_representativeandconst(self):
        self.representative = oa.get_representatives(int(self.postcode))[0]['full_name']
        self.constituency = oa.get_representatives(self.postcode)[0]['constituency']
        self.personid = oa.get_representatives(self.postcode)[0]['person_id']

    def openaustraliadata(self):
        return oa.get_representatives(self.postcode)


    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Hansard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    majorheading = db.relationship('MajorHeading', backref='hansard', lazy='dynamic')

    def __repr__(self):
        return '<Hansard {}>'.format(self.body)

class MajorHeading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hansard_id = db.Column(db.Integer, db.ForeignKey('hansard.id'))
    minorheading = db.relationship('MinorHeading', backref='majorheading', lazy='dynamic')
    body = db.Column(db.String(140))

    def __repr__(self):
        return '<MajorHeading {}>'.format(self.body)

class MinorHeading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    major_heading = db.Column(db.Integer, db.ForeignKey('majorheading.id'))
    speech = db.relationship('Speech', backref='minorheading', lazy='dynamic')
    body = db.Column(db.String(140))

    def __repr__(self):
        return '<MinorHeading {}>'.format(self.body)

class Speech(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(10000))
    def __repr__(self):
        return '<Speech {}>'.format(self.body)
