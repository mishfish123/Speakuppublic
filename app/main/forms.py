from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, HiddenField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length,Regexp
from app.models import User

class EditProfileForm(FlaskForm):
    '''Form which allows users to edit their profile page'''
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    postcode = StringField('Postcode', validators=[Length(min=0, max=4), Regexp("^(?:(?:[2-8]\d|9[0-7]|0?[28]|0?9(?=09))(?:\d{2}))$")],render_kw={"placeholder": "Postcode"}) #makes sure the entry matches a regex expression of Australian postcodes
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        '''saves the users original username in a variable which can be used in the validate_username validator down below'''
        super(EditProfileForm, self).__init__(*args, **kwargs) #ensures previous initialisation procedures are followed
        self.original_username = original_username #saves the users original username in original username

    def validate_username(self, username):
        '''validates that the username doesnt exist in the database or is the users original user name'''
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None: #if an entry is returned from the data base
                raise ValidationError('Please use a different username.')

class EmptyForm(FlaskForm):
    '''an empty form which allows the following and unfollowing functions to ensue'''
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    '''form which allows users to comment on specific debates'''
    identifier = StringField()
    post = TextAreaField('Say something', validators=[DataRequired()])
    hidden = TextAreaField("Field 2",id="srcLibArticles")
    submit = SubmitField('Submit')

class DateForm(FlaskForm):
    '''form which allows users to submit which hansard to view based on its date'''
    identifier = StringField()
    date = DateField("Select another date", id="datepicker",format='%m/%d/%Y') #formats the date using the notation month/day/year
    submit = SubmitField('Change date')

class SearchForm(FlaskForm):
    '''form which allows users the search hansards and other user comments'''
    q = StringField('Search', validators=[DataRequired()])
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class MessageForm(FlaskForm):
    '''form which allows users to send private messages to another person'''
    message = TextAreaField(('Message'), validators=[Length(min=1, max=140)])
    submit = SubmitField(('Submit'))
