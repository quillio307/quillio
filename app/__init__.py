from flask import Flask, render_template
from flask_security import Security, login_required

# Blueprints
from app.modules.auth.controller import auth
from app.modules.meeting.controller import meeting
#from app.modules.note.controller import note

# Security
from app.modules.auth.model import user_datastore

# Setup
from app import config
from app.setup import login_manager, db

app = Flask(__name__)
app.config.from_pyfile(config.CONFIG_PATH)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(meeting, url_prefix='/meeting')
#app.register_blueprint(note, url_prefix='/note')

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
