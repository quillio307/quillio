SECRET_KEY = '907a9219e42a731955df7c4f73b79d7ae26db3825f97f700'

# Database configuration
MONGODB_SETTINGS = {
    'db': 'quillio',
    'host': 'mongodb://localhost:27017/quillio'
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
