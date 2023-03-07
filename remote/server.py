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

import datetime
import json
import authenticate
import sqlite3
import files
import os

# Create the app
app = flask.Flask(__name__)

PORT = 5005

DATABASE = 'database/storage.db'
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys')
SSL_CONTEXT = (os.path.join(ASSETS_DIR,'server.crt'), os.path.join(ASSETS_DIR,'server.key'))

app.register_error_handler(authenticate.AuthenticationError,
                           lambda e : ("{}", 403))

# Integrity Errors can only happen for the user if there is a conflict when
# creating a username, so 409 Conflict is appropriate
app.register_error_handler(sqlite3.IntegrityError,
                           lambda e: ("", 409))

# This happens if the JSON or form contains or does not contain
app.register_error_handler(KeyError, lambda e : ("", 400))

app.register_error_handler(FileNotFoundError, lambda e : ("", 404))


@app.route("/user/auth", methods=["POST"])
def auth_user():
    """Used for authenticating the user.

    Methods:
        POST:
            Username
                -- The user's username
            Password
                -- The user's password

    Arguments:
        None

    Returns:
        response: flask.Response
            -- The response, it has the added header of set-cookie
    """

    connection = sqlite3.connect(DATABASE)
    with connection:
        username = flask.request.form.get('Username')
        password = flask.request.form.get('Password')
        if username is None or password is None:
            flask.abort(400)

        user_ID = ""
        user_ID = authenticate.auth_username_password(username, password, connection)

        session_ID, expires = authenticate.create_session(user_ID, connection)

        resp = flask.make_response("")
        resp.set_cookie('SessionID', bytes(session_ID, "UTF-8"), expires=expires)
    return resp


@app.route('/user/create', methods=['POST'])
def create_user():
    """Used for creating a new user.

        Methods:
            POST:
                Username
                    -- The user's username
                Password
                    -- The user's password

        Arguments:
            None

        Returns:
            response: flask.Response
                -- The response, it has the added header of set-cookie
        """
    connection = sqlite3.connect(DATABASE)
    with connection:
        username = flask.request.form.get('Username')
        password = flask.request.form.get('Password')
        if username is None or password is None:
            flask.abort(400)
        user_ID = authenticate.create_user(username, password, connection)
        session_ID, expires = authenticate.create_session(user_ID, connection)
        expires = datetime.datetime.fromisoformat(expires)

        resp = flask.make_response("")
        resp.set_cookie('SessionID', bytes(session_ID, "UTF-8"), expires=expires)

    return resp


@app.route("/file/add", methods=["POST"])
def add_file():
    if "SessionID" not in flask.request.cookies:
        raise authenticate.AuthenticationError
    connection = sqlite3.connect(DATABASE)
    with connection:
        session_ID = flask.request.cookies['SessionID']
        user_ID = authenticate.auth_session(session_ID, connection)
        filename = flask.request.form.get("Filename")
        description = flask.request.form.get("Description")
        filepath = files.create_file(user_ID, filename, description, connection)
    return json.dumps({'Filepath': filepath})


@app.route("/file/update", methods=["POST"])
def update_file():
    if "SessionID" not in flask.request.cookies:
        raise authenticate.AuthenticationError
    connection = sqlite3.connect(DATABASE)
    with connection:
        session_ID = flask.request.cookies['SessionID']
        user_ID = authenticate.auth_session(session_ID, connection)
        data = json.loads(flask.request.get_data())
        filepath = data["Filepath"]
        filename = data["Filename"]
        description = data["Description"]
        content = data["Content"]
        files.update_file(filepath, user_ID, filename, description, content, connection)
    return ""


@app.route("/file/get-all", methods=["GET"])
def get_all_files():
    """Used for getting a list of all the files

    Methods:
        GET

    Arguments:
        None

    Returns:
        response: str
            -- The response. It is of the format:
                {“Files”: [
                    {
                        "Filepath": <File path>,
                        "Filename": <File name>,
                        "Description": <File description>
                    }, ...
                ]}
    """

    if "SessionID" not in flask.request.cookies:
        raise authenticate.AuthenticationError
    connection = sqlite3.connect(DATABASE)
    with connection:
        session_ID = flask.request.cookies['SessionID']
        user_ID = authenticate.auth_session(session_ID, connection)
        files_ = files.get_all_files(user_ID, connection)
        out = []
        for filepath, filename, description in files_:
            out.append({'Filepath': filepath, 'Filename': filename,
                        'Description': description})
    return json.dumps({'Files': out})


@app.route("/file/get-one/<filepath>")
def get_one_file(filepath):
    """Used for getting a single file

    Methods:
        GET

    Arguments:
        filepath:
            -- The path of the file to et

    Returns:
        response: str
            -- The response. It is of the format:
                {
                    "Filepath": <File path>,
                    "Content": <Content>
                }
    """
    if "SessionID" not in flask.request.cookies:
        raise authenticate.AuthenticationError
    connection = sqlite3.connect(DATABASE)
    with connection:
        session_ID = flask.request.cookies['SessionID']
        user_ID = authenticate.auth_session(session_ID, connection)
        content = files.read_file(filepath, user_ID, connection)
        if content is None:
            raise authenticate.AuthenticationError
        filename, description = files.get_particular_file(filepath, user_ID, connection)

    return json.dumps({"Filepath": filepath, "Filename": filename, "Description": description, "Content": content})


@app.route('/')
def root():
    return "Test successful"


if __name__ == '__main__':
    app.run(host="localhost", port=PORT, ssl_context=SSL_CONTEXT)
