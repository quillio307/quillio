from flask import Flask, render_template, redirect, url_for
from flask_mongoengine import MongoEngine

# Initialize the app
app = Flask(__name__)
app.config.from_object('config')


# Jenna's Code
# app.config['SENDGRID_API_KEY'] = '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'
# app.config['SENDGRID_DEFAULT_FROM'] = "quillio.admin@quillio.com"

# mail = SendGrid(app) 


# Define the database
db = MongoEngine(app)


@app.route('/')
def index():
    return '<h1> Quillio Home </h1>'


# Import Blueprint modules
from app.modules.auth.controller import auth
from app.modules.group.controller import group
from app.modules.meeting.controller import meeting

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(group, url_prefix='/groups')
app.register_blueprint(meeting, url_prefix='/meetings')
