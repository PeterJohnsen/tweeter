#!/usr/bin/env python
from flask import Flask, render_template, url_for, redirect, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import check_password_hash

from config import *
import models
from forms import SignupForm, LoginForm, TweetForm


app = Flask(__name__)
app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    signup_form = SignupForm()
    login_form = LoginForm()
    return render_template('index.html', signup_form=signup_form, login_form=login_form)


@app.route('/signup', methods=['POST'])
def signup():
    signup_form = SignupForm()
    if signup_form.validate_on_submit():
        models.User.create_user(
                input_name=signup_form.name.data,
                input_email=signup_form.email.data,
                input_username=signup_form.username.data,
                input_password=signup_form.password.data
        )
        flash('Welcome to tweeter! :)', 'success')

        # automatically login users right after signup
        user = models.User.get(models.User.username**signup_form.username.data)
        login_user(user)
        return render_template('dashboard.html')
    else:
        login_form = LoginForm(None) # to render indexpage with empty login form
        return render_template('index.html', signup_form=signup_form, login_form=login_form)


@app.route('/login', methods=['POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        try:
            user = models.User.get(models.User.email==login_form.email.data)
        except models.DoesNotExist:
            flash('Incorrect Email or Password', 'danger')
        else:
            if check_password_hash(user.password, login_form.password.data):
                login_user(user)
                return render_template('dashboard.html')
            else:
                flash('Incorrect Email or Password', 'danger')

    signup_form = SignupForm(None) # to render indexpage with empty SignupForm
    return render_template('index.html', signup_form=signup_form, login_form=login_form)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    login_form = LoginForm()
    signup_form = SignupForm()
    flash('We will miss you. :(', 'success')
    return render_template('index.html', login_form=login_form, signup_form=signup_form)


@app.route('/tweet', methods=['GET', 'POST'])
@login_required
def tweet():
    tweet_form = TweetForm()
    if tweet_form.validate_on_submit():
        models.Tweet.create(
                user=current_user._get_current_object(),
                content=tweet_form.content.data.strip()
        )
        flash('You just tweeted. :)', 'success')
        return redirect(url_for('index'))

    return render_template('tweet.html', tweet_form=tweet_form)



@app.before_request
def before_request():
    models.database.connect()


@app.after_request
def after_request(response):
    models.database.close()
    return response


if __name__ == '__main__':
    models.initialise()
    app.run(debug=DEBUG, host=HOST, port=PORT)
