from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, HiddenField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length, Regexp
from app.models import User


class LoginForm(FlaskForm):
    '''Form used to login users'''
    username = StringField('Username', validators=[DataRequired()],render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    '''Form used to register users'''
    username = StringField('Username', validators=[DataRequired()],render_kw={"placeholder": "Username"})
    postcode = StringField('Postcode', validators=[Length(min=0, max=4), Regexp("^(?:(?:[2-8]\d|9[0-7]|0?[28]|0?9(?=09))(?:\d{2}))$")],render_kw={"placeholder": "Postcode"})
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')],render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        '''custom validation method to ensure there are no duplicate usernames in database'''
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        '''custom validation method to ensure there are no duplicate emails in database'''
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ResetPasswordRequestForm(FlaskForm):
    '''Form to email user a password token'''
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    '''Form to reset user's password once token is recieved'''
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
