from wtforms.validators import ValidationError

from models import User


class EntryMustNotExist():
    def __init__(self, form, field):
        if User.select().where(getattr(User, field.label.text)**field.data).exists():
            error_message = 'A user with {0} as {1} already exists'.format(field.label.text, field.data)
            raise ValidationError(error_message)


