from flask import Flask, render_template
from flask_login import login_required

from app.modules.auth.controller import auth
from config import login_manager


app = Flask(__name__)
app.secret_key = 'super secret key'
app.session_type = 'mongodb'

login_manager.init_app(app)

app.register_blueprint(auth, url_prefix='/auth')


@app.route('/')
@login_required
def home():
    return render_template('index.html')
