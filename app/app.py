from flask import Flask
from flask import request
import os
import pymongo
from pymongo import MongoClient

app = Flask(__name__)

MONGODB_URI = os.environ.get('MONGODB_URI')
if not MONGODB_URI:
    MONGODB_URI = None

mongo = MongoClient(MONGODB_URI)
db = mongo['heroku_4b10n3s4']  # Core database


@app.route('/', methods=['GET'])
def landing_page():
    print(db['Test'].find_one())  # Should print foo: bar
    return 'Welcome to quillio!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return "You are logged in!"
    elif request.method == 'GET':
        return "Would you like to login?"


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        return "Goodbye!"


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if request.method == 'GET':
        return "Here is your dashboard"
