import sys
import unittest
from app import app, socketio

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        tests = unittest.TestLoader().discover('app/tests', pattern=("test*.py"))
        result = unittest.TextTestRunner(verbosity=2).run(tests)
    else:
        socketio.run(app, debug=True, port=5000)
