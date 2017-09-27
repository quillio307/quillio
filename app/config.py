import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config.py')

SECRET_KEY = '8616775396515539'

MONGODB_SETTINGS = {
    'db': 'heroku_4b10n3s4',
    'host': 'mongodb://heroku_4b10n3s4:ldlbj6d3it0u3n5un9kb9d38n9@ds147884.mlab.com:47884/heroku_4b10n3s4'
}

SECURITY_LOGIN_URL = '/auth/login'

SECURITY_REGISTER_URL = '/auth/signup'
