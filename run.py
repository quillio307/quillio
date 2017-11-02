from app import app, socketio

socketio.run(app, debug=True, port=5000)
