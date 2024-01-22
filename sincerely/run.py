from chatapp import create_app, socketio

# create app from returned app in create_app function (see _init_)
app = create_app()

# run app
socketio.run(app)
