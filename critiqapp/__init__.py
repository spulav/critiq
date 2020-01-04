from flask import Flask
import random

app = Flask(__name__)

app.config['PERMANENT_SESSION_LIFETIME'] = 300000
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['SECRET_KEY'] = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])
app.config['UPLOAD_FOLDER'] = '/uploaded/'

import critiqapp.critiq