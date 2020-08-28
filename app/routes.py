from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/',methods = ['GET', 'POST'])
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)



@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('signin.html', title = "Sign In", form=form)
