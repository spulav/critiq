from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import (InputRequired, Email)

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email',
        validators=[InputRequired(), 
                    Email(message='Enter a valid email.')]
    )

    submit = SubmitField('Reset Password')