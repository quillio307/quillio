from app import socketio
from app import app

#app.run(port=5000)
socketio.run(app, debug=True, port=5000)