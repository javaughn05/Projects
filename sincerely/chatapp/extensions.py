from flask_socketio import SocketIO

# allows for cross origin request from any domain
socketio = SocketIO(cors_allowed_origins="*")
