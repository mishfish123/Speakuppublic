from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length, Regexp
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],render_kw={"placeholder": "Username"})
    postcode = StringField('Postcode', validators=[Length(min=0, max=4), Regexp("^(?:(?:[2-8]\d|9[0-7]|0?[28]|0?9(?=09))(?:\d{2}))$")],render_kw={"placeholder": "Postcode"})
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')],render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    postcode = StringField('Postcode', validators=[Length(min=0, max=4), Regexp("^(?:(?:[2-8]\d|9[0-7]|0?[28]|0?9(?=09))(?:\d{2}))$")],render_kw={"placeholder": "Postcode"})
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired()])
    hidden = TextAreaField("Field 2",id="srcLibArticles")
    submit = SubmitField('Submit')
