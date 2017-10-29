from flask import Flask, render_template, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO

# Initialize the app
app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=True)

# Define the database
db = MongoEngine(app)


@app.route('/')
def index():
    return '<h1> Quillio Home </h1>'


# Import Blueprint modules
from app.modules.auth.controller import auth
from app.modules.group.controller import group
from app.modules.meeting.controller import meetings
from app.modules.meeting.in_meeting import meeting

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(group, url_prefix='/groups')
app.register_blueprint(meetings, url_prefix='/meetings')
app.register_blueprint(meeting, url_prefix='/meeting')
