from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import (InputRequired,Email,EqualTo,Length)

class SignUpForm(FlaskForm):
    username = StringField('Username',
        validators=[InputRequired()]
    )

    email = StringField('Email',
        validators=[Length(min=6),
                    Email(message='Enter a valid email.'),
                    InputRequired()]
    )

    password = PasswordField('Password',
        validators=[InputRequired(),
                    Length(min=6, message='Select a stronger password.')]
    )

    confirm = PasswordField('Confirm Your Password',
        validators=[
            InputRequired(),
            EqualTo('password', message='Passwords must match.')]
    )
