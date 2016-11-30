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
@app.route('/<username>', methods=['GET'])
def index(username=None):
    login_form = LoginForm()
    if username or current_user.is_authenticated:
        tweet_form = TweetForm()
        if username:
            user = models.User.get(models.User.username**username)
        else:
            user = current_user._get_current_object()
        return render_template('dashboard.html', user=user, login_form=login_form, tweet_form=tweet_form)

    signup_form = SignupForm()
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
        return redirect(url_for('index'))
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
                return redirect(url_for('index'))
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
    flash('We will miss you. :(', 'note')
    return render_template('index.html', login_form=login_form, signup_form=signup_form)


@app.route('/tweet', methods=['GET', 'POST'])
@login_required
def tweet():
    tweet_form = TweetForm()
    if tweet_form.validate_on_submit():
        with models.database.transaction():
            models.Tweet.create(
                    user=current_user._get_current_object(),
                    content=tweet_form.content.data.strip()
            )
        flash('You just tweeted. :)', 'success')
        return redirect(url_for('index'))

    return render_template('tweet.html', tweet_form=tweet_form)


@app.route('/tweets', methods=['GET'])
@app.route('/tweets/<tweet_id>', methods=['GET'])
def tweets(tweet_id=None):
    tweets = models.Tweet.select()
    login_form = LoginForm()
    return render_template('tweets.html', tweets=tweets, login_form=login_form)


@app.route('/fav_tweets', methods=['GET'])
@login_required
def fav_tweets():
    tweets = models.Tweet.select().where(models.Tweet.user << current_user.get_followees())

    if (tweets.count() == 0):
        flash('You are not following anyone yet.', 'note')

    login_form = LoginForm()
    return render_template('tweets.html', tweets=tweets, login_form=login_form)


@app.route('/follow/<username>', methods=['GET'])
@login_required
def follow(username):
    try:
        followee = models.User.get(models.User.username**username)
    except DoesNotExist:
        flag('No such user', 'danger')
        return redirect(url_for('index'))
    else:
        try:
            with models.database.transaction():
                models.Relationship.create(
                        follower=current_user._get_current_object(),
                        followee=followee
                )
        except models.IntegrityError:
            pass
        else:
            flash('You are now following {}!'.format(username), 'success')
    return redirect(url_for('index', username=username))

        
@app.route('/unfollow/<username>', methods=['GET'])
@login_required
def unfollow(username):
    try:
        followee = models.User.get(models.User.username**username)
    except DoesNotExist:
        flag('No such user', 'danger')
        return redirect(url_for('index'))
    else:
        try:
            models.Relationship.get(
                    models.Relationship.follower==current_user._get_current_object(),
                    models.Relationship.followee==followee
            ).delete_instance()
        except models.DoesNotExist:
            pass
        else:
            flash('You unfollowed {}!'.format(username), 'note')
    return redirect(url_for('index', username=username))


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
