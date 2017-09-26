# Setup
import config
from setup import login_manager, db

from flask import Flask, render_template
from flask_security import Security, login_required, \
                            roles_required, roles_accepted

# Blueprints
from app.modules.auth.controller import auth

# Security
from app.modules.auth.model import user_datastore

app = Flask(__name__)
app.config.from_pyfile(config.CONFIG_PATH)

app.register_blueprint(auth, url_prefix='/auth')


login_manager.init_app(app)
db.init_app(app)
security = Security(app, user_datastore)


@app.route('/')
def index():
    return '<h1> Quillio Home </h1>'


@app.route('/home')
@login_required
def home():
    return render_template('index.html')
