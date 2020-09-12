from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, HiddenField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length,Regexp
from app.models import User

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
    identifier = StringField()
    post = TextAreaField('Say something', validators=[DataRequired()])
    hidden = TextAreaField("Field 2",id="srcLibArticles")
    submit = SubmitField('Submit')

class DateForm(FlaskForm):
    identifier = StringField()
    date = DateField("Select another date", id="datepicker",format='%m/%d/%Y')
    submit = SubmitField('Change date')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class MessageForm(FlaskForm):
    message = TextAreaField(('Message'), validators=[Length(min=1, max=140)])
    submit = SubmitField(('Submit'))
