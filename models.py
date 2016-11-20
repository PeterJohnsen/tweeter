import datetime

from peewee import *
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin

from config import *


database = SqliteDatabase(DATABASE)


class User(UserMixin, Model):
    name = CharField(max_length=30)
    username = CharField(unique=True, max_length=18)
    email = CharField(unique=True)
    password = CharField(max_length=20)
    joined_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = database
        order_by = ('joined_at',)

    @classmethod
    def create_user(cls, input_name, input_email, input_username, input_password):
        cls.create(name=input_name, email=input_email, username=input_username, password=generate_password_hash(input_password))


 class Tweet(Model):
     timestamp = DateTimeField(dafault=datetime.datetime.now)
     user = ForeignKeyField(User, 'tweets')
     content = TextField()

     class Meta:
         database = database
         order_by = ('-timestamp',)


def initialise():
    database.connect()
    database.create_tables([User], safe=True)
    database.close()
