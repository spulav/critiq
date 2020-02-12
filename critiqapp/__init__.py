from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from .dashboard import board
from .logins import login
#from .profile import profile
#from .read import read

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object('config')
    
    from critiqapp.lookup import db
    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(login)
    #app.register_blueprint(board, url_prefix='/dashboard')
    #app.register_blueprint(profile, url_prefix='/profile')
    #app.register_blueprint(read)

    #import critiqapp.critiq (extra code -- to delete later)

    return app