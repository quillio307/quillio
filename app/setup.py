from flask_login import LoginManager
from flask_mongoengine import MongoEngine

login_manager = LoginManager()

db = MongoEngine()
