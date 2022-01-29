from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # app configuration
    flask_env = os.getenv("FLASK_ENV", None)

    if flask_env == "development":
        app.config.from_object("config.DevConfig")
    elif flask_env == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.ProductionConfig")

    # initialize plug-ins
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from . import dbmodels

    # app context
    with app.app_context():
        # initialize database
        db.create_all()

        # blueprints
        import routes
        
        app.register_blueprint(routes.auth_bp)
        app.register_blueprint(routes.board_bp)

        return app