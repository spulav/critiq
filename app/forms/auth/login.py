from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (InputRequired, Email)

class LoginForm(FlaskForm):
    email = StringField('Email',
        validators=[InputRequired(), 
                    Email(message='Enter a valid email.')]
    )
    
    password = PasswordField('Password',
        validators=[InputRequired()]
    )

    submit = SubmitField('Log In')

