from flask import Flask
#from .dashboard import board
from .logins import login
#from .profile import profile
#from .read import read

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.config.from_object('config')

import critiqapp.critiq
# ============== Registrations =============
#app.register_blueprint(board, url_prefix='/dashboard')
app.register_blueprint(login)
#app.register_blueprint(profile, url_prefix='/profile')
#app.register_blueprint(read)