"""This is the remote server for cloud storage.

It is implemented as a flask web server despite not being actually a web
server. This is for simplicity and security.

Endpoints:
    /user/auth
        -- For authenticating users
    /file/add
        -- For adding a new, empty file
    /file/update
        -- For updating existing files
    /file/get-all
        -- For getting a list of all the files
    /file/get-one/<filepath>
        -- For getting the content of a particular file

Cookies:
    SessionID:
        -- The session ID
"""

import flask

# Create the app
app = flask.Flask(__name__)


@app.route("/user/auth", methods=["POST"])
def auth():
    """Used for authenticating the user."""