from flask import Flask, render_template
from flask_login import LoginManager

from app.modules.auth.controller import auth

app = Flask(__name__)

app.register_blueprint(auth, url_prefix='/auth')

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def home():
    return render_template('index.html')
