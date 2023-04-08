import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    #UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DB_URI")

class ProductionConfig(Config):
    DEBUG = False

class DevelopConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True