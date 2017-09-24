from flask import Flask, render_template
from mongoengine import connect

from config import MONGODB_SETTINGS

# Enpoints
from app.modules.auth.controller import auth


app = Flask(__name__)


connect(MONGODB_SETTINGS['db'], host=MONGODB_SETTINGS['host'])

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')


@app.route('/')
def home():
    return render_template('index.html')
