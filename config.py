import random

PERMANENT_SESSION_LIFETIME = 300000
TRAP_BAD_REQUEST_ERRORS = True
SECRET_KEY = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])
UPLOAD_FOLDER = '/uploaded/'