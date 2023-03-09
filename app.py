"""This is the main 'app' file for the Client's Flask server.

It is a typical HTTP flask server run for localhost on port 5000.

Endpoints:
    /
        -- Redirects to /calculator
    /login
        -- Login form. Successful login directs to /calculator
    /signup
        -- Sign up form. Successful signing up directs to /calculator
    /calculator
        -- The calculator. Can log out and redirect to /login. Will also be
           able to redirect to /saved-graphs
    /saved-graphs
        -- Not implemented

Cookies:
    height -- The height of the graph in pixels
    width  -- The width of the graph in pixels

Functions:
    root() -> None
        -- For '/' endpoint
    login() -> None
        -- For '/login' endpoint
    signup() -> None
        -- For '/signup' endpoint
    calculator() -> None
        -- For '/calculator' endpoint
    saved_graphs() -> None
        -- Not implemented

Global variables:
    app: flask.Flask
        -- The flask application
    PORT: int
        -- The port the server runs on
    X_RANGE: tuple[int, int]
        -- The range of x-values on the graph
    Y_range: tuple[int, int]
        -- The range of y-values on the graph
"""

# Import flask for the server
import flask

# Import the local module 'evaluator' for evaluating the graphing statement
import evaluator

import client_cloud_storage

# The flask app
app = flask.Flask(__name__)

cloud_storage = client_cloud_storage.CloudStorage()
calculator_path = ""
path = "static/default.png"
prev_raw_text = ""
# The port the flask app is hosted on
PORT = 5000

# The range of X and Y values on the graph
X_RANGE = (-5, 5)
Y_RANGE = (-5, 5)





@app.route('/')
def root():
    """The function that redirects the root template to /calculator

    Arguments:
        None

    Returns:
        response: flask.BaseResponse
            -- The response
    """
    return flask.redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """The function that renders the 'login' form

    Methods:
        GET

    Arguments:
        None

    Returns:
        HTML_content: str
            -- The rendered HTML for login

    """

    if flask.request.method == 'POST':
        try:
            username = flask.request.form['username']
            password = flask.request.form['password']
            cloud_storage.authorise_user(username, password)
        except client_cloud_storage.AuthorisationError:
            return flask.render_template('login.html', error_message="Username or Password is incorrect")
        return flask.redirect('/calculator')

    return flask.render_template('login.html', error_message="")


@app.route('/signup', methods=['GET','POST'])
def signup():
    """The function that renders the 'signup' form

    Methods:
        GET

    Arguments:
        None

    Returns:
        HTML_content: str
            -- The rendered HTML for signup
    """
    if flask.request.method == 'POST':
        try:
            username = flask.request.form['username']
            password = flask.request.form['password']
            password_again = flask.request.form['password-again']
            if password != password_again:
                return flask.render_template('signup.html', error_message="Passwords do not match")
            cloud_storage.create_user(username, password)
            return flask.redirect('/calculator')
        except client_cloud_storage.ConflictError:
            return flask.render_template('signup.html', error_message="User already exists")
    return flask.render_template('signup.html')


@app.route('/calculator', methods=['GET', 'POST'])
@app.route('/calculator/<filepath>', methods=['GET', 'POST'])
def calculator(filepath=""):
    """The function that renders the 'calculator' page.
    It also calls on the evaluator to evaluate the text.

    Methods:
        GET
        POST:
            raw_text: textbox
                -- The text that will be evaluated for graphing

    Arguments:
        filepath: str
            -- The path of the file

    Returns:
        HTML_content: str
            -- The HTML content of the calculator page
    """

    global calculator_path
    global path
    global prev_raw_text

    # Initilise the raw text and the path.
    # Raw text has to be initilised because it is then fed back into the
    # template so the user can easily modify the graph
    raw_text = prev_raw_text
    filename = ""
    description = ""
    error_message = ""
    minx = X_RANGE[0]
    maxx = X_RANGE[1]
    miny = Y_RANGE[0]
    maxy = Y_RANGE[1]

    calculator_path = filepath
    if filepath:
        calculator_path = "/" + filepath

    if filepath and flask.request.method == 'GET':
        try:
            filename, description, raw_text = cloud_storage.get_one_file(filepath)
        except client_cloud_storage.AuthorisationError:
            error_message = "Unable to open file: access denied"

    if flask.request.method == 'POST' and flask.request.form['for'] == 'save':
        content = flask.request.form['content']
        filename = flask.request.form['filename']
        description = flask.request.form['description']
        if filepath == "":
            filepath = cloud_storage.create_file(filename, description)
            cloud_storage.update_file(filepath, filename, description, content)
        else:
            try:
                cloud_storage.update_file(filepath, filename, description, content)
            except client_cloud_storage.AuthorisationError:
                error_message = 'Unauthorised to save graph'
        return flask.redirect(f'/calculator/{filepath}')

    # Only try to graph if the user has just submitted a form
    if flask.request.method == 'POST' and flask.request.form['for'] == 'graph':

        # First, get the raw text from the form
        raw_text = flask.request.form['raw_text']
        filename = flask.request.form['filename2']
        description = flask.request.form['description2']
        prev_raw_text = raw_text

        minx = flask.request.form['min-x']
        maxx = flask.request.form['max-x']
        miny = flask.request.form['min-y']
        maxy = flask.request.form['max-y']

        # Get the height and width of the graph in pixels.
        # If they are not valid integers Default to a height of 0 and a width
        # of 0
        try:
            height = int(flask.request.cookies['height'])
            width = int(flask.request.cookies['width'])
        except ValueError:
            height = 0
            width = 0

        try:
            minx = float(minx)
            maxx = float(maxx)
            miny = float(miny)
            maxy = float(maxy)
        except ValueError:
            minx = -5
            maxx = 5
            miny = -5
            maxy = 5

        # If, somehow, the height and width are negative, make them positive
        if height < 0:
            height = 0
        if width < 0:
            width = 0

        # Evaluate these and get the path of the file where they are stored
        path, error_message = evaluator.evaluate(raw_text, width, height, (minx, maxx), (miny, maxy))

    # Finally render the 'calculator.html' template substituting in raw_text
    # for the raw text on the form and path for the imate location
    return flask.render_template(
        'calculator.html',
        raw_text=raw_text,
        filename=filename,
        description=description,
        error_message=error_message,
        calculator_path=calculator_path,
        image_location=path,
        minx=minx,
        maxx=maxx,
        miny=miny,
        maxy=maxy)


# Not implemented
@app.route('/saved-graphs')
def saved_graphs():
    try:
        graphs = cloud_storage.get_all_files()
        return flask.render_template('saved_graphs.html',
                                     graphs=graphs,
                                     calculator_path=calculator_path,)
    except client_cloud_storage.AuthorisationError:
        return flask.redirect('/login')


# If running the file directly, host the flask server locally on the default
# port. It is currently in debug mode as that allows for easy debugging.
if __name__ == '__main__':
    app.run(host='localhost', port=PORT, debug=False)
