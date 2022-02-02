from app import mail
from flask_mail import Message
from flask import render_template
import os
from app.dbmodels import User
from dotenv import load_dotenv

def forgot_password_email(user):
    token = user.get_token()
    msg = Message()
    msg.subject = "Critiq Password Reset"
    msg.sender = os.environ.get('MAIL_USERNAME')
    msg.recipients = [user.email]
    msg.html = render_template('auth/reset_email.html',
                                token=token)
    mail.send(msg)