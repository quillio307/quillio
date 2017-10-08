# Database configuration
MONGODB_SETTINGS = {
    'db': 'heroku_4b10n3s4',
    'host': 'mongodb://heroku_4b10n3s4:ldlbj6d3it0u3n5un9kb9d38n9@ds147884.mlab.com:47884/heroku_4b10n3s4'
}

# Define the threads per page, usually 2
THREADS_PER_PAGE = 2

# Security Configuration
SECRET_KEY = '907a9219e42a731955df7c4f73b79d7ae26db3825f97f700'

SECURITY_POST_LOGIN_VIEW = '/meetings'
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_PASSWORD_SALT = 'asdfkashdfjshgfajsdfakshfashdflashflashdgfaksflasfakshjhsbfiawvelifhsbjhvasgfuwfqvgwvfhsgvdjasgf'
