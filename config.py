SECRET_KEY = '907a9219e42a731955df7c4f73b79d7ae26db3825f97f700'

# Database configuration
MONGODB_SETTINGS = {
    'db': 'heroku_4b10n3s4',
    'host': 'mongodb://heroku_4b10n3s4:ldlbj6d3it0u3n5un9kb9d38n9@ds147884.mlab.com:47884/heroku_4b10n3s4'
}

# Define the threads per page, usually 2
THREADS_PER_PAGE = 2


# Security Configuration
SECURITY_URL_PREFIX = '/'

SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_PASSWORD_SALT = 'b48a8f1418bd81b0a760820b5f25a637d1fcd2a06e5d9a18f51d16d6bfa3584877f4f7c7294bb60b18a80622d12f6155b3969e29c0e6f8694deef0936da1e239'

SECURITY_REGISTER_URL = '/auth/signup'
SECURITY_LOGIN_URL = '/auth/login'

SECURITY_REGISTER_USER_TEMPLATE = 'auth/signup.html'
SECURITY_LOGIN_USER_TEMPLATE = 'auth/login.html'

SECURITY_POST_LOGIN_VIEW = '/meetings'
SECURITY_POST_REGISTER_VIEW = '/meetings'
SECURITY_POST_LOGOUT_VIEW = '/'

# Mail Configuration
SENDGRID_API_KEY = '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'
SENDGRID_DEFAULT_FROM = "noreply@quillio.com"