from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired, Length, Regexp, EqualTo

from customvalidators import EntryMustNotExist

class SignupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('email', validators=[DataRequired(), Email(), EntryMustNotExist])
    username = StringField('username', validators=[
                                            DataRequired(), 
                                            EntryMustNotExist,
                                            Regexp(
                                                r'^[a-zA-Z0-9_]+$',
                                                message="Usename must not contain any special character except underscore"
                                            ),
                                            Length(min=3, max=18)
                                       ]
               )
    password = PasswordField('password', validators=[
                                            DataRequired(),
                                            Length(min=5),
                                            EqualTo('password2', message="Password doesn't match")
                                         ]
               )
    password2 = PasswordField('re-type Password', validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=5)])


