import sys 
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO

# Initialize the app
app = Flask(__name__)
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    app.config.from_object('config_test')
else:
    app.config.from_object('config')
socketio = SocketIO(app, logger=True)

# Define the database
db = MongoEngine(app)


@app.route('/')
def index():
    return '<h1> Quillio Home </h1>'


# Import Blueprint modules
from app.modules.auth.controller import auth
from app.modules.groups.controller import groups
from app.modules.meetings.controller import meetings
from app.modules.meetings.in_meeting import meeting
from app.modules.profile.controller import profile

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(groups, url_prefix='/groups')
app.register_blueprint(meetings, url_prefix='/meetings')
app.register_blueprint(meeting, url_prefix='/meeting')
app.register_blueprint(profile, url_prefix='/profile')
