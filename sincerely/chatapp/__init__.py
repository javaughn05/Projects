from flask import Flask

# !? from flask_session import Session !?
from .events import socketio
from .routes import main

# creates application
def create_app():
    # configure application
    app = Flask(__name__)
    # reloads changes made to applicaton and provide message in terminal when error occurs
    app.config["DEBUG"] = True
    # cryptographic key used to generate signatures of users
    app.config["SECRET_KEY"] = "secret"

    # blueprint organizes groups of related routes; registers that blueprint
    app.register_blueprint(main)

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"

    # initializes the app via its socket connection
    socketio.init_app(app)

    # configures application hosted on Flask server
    return app


