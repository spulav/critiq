from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import (InputRequired, EqualTo,Length)

class NewPassword(FlaskForm):
    password = PasswordField('New Password',
        validators=[InputRequired(),
                    Length(min=6, message='Select a stronger password.')]
    )

    confirm = PasswordField('Confirm Your Password',
        validators=[
            InputRequired(),
            EqualTo('password', message='Passwords must match.')]
    )

    submit = SubmitField('Confirm')
