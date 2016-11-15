#!/usr/bin/env python
from flask import Flask, render_template, url_for, redirect, flash

from config import *
import models
from forms import SignUpForm


app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/', methods=['GET'])
def index():
    form = SignUpForm()
    return render_template('index.html', form=form)


@app.route('/signup', methods=['POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        models.User.create_user(
                input_name=form.name.data,
                input_email=form.email.data,
                input_username=form.username.data,
                input_password=form.password.data
        )
        flash('Yay, you are in now! Please Sign In to continue. :D', 'success')
    return render_template('index.html', form=form)


if __name__ == '__main__':
    models.initialise()
    app.run(debug=DEBUG, host=HOST, port=PORT)
