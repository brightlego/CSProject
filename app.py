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

# The flask app
app = flask.Flask(__name__)

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
    return flask.redirect('/calculator')


@app.route('/login')
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
    return flask.render_template('login.html')


@app.route('/signup')
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
    return flask.render_template('signup.html')


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    """The function that renders the 'calculator' page.
    It also calls on the evaluator to evaluate the text.

    Methods:
        GET
        POST:
            raw_text: textbox
                -- The text that will be evaluated for graphing

    Arguments:
        None

    Returns:
        HTML_content: str
            -- The HTML content of the calculator page
    """

    # Initilise the raw text and the path.
    # Raw text has to be initilised because it is then fed back into the
    # template so the user can easily modify the graph
    raw_text = ""
    path = "static/test.png"  # static/test.png contains the placeholder image

    # Only try to graph if the user has just submitted a form
    if flask.request.method == 'POST':

        # First, get the raw text from the form
        raw_text = flask.request.form.get('raw_text')

        # Get the height and width of the graph in pixels.
        # If they are not valid integers Default to a height of 0 and a width
        # of 0
        try:
            height = int(flask.request.cookies['height'])
            width = int(flask.request.cookies['width'])
        except ValueError:
            height = 0
            width = 0

        # If, somehow, the height and width are negative, make them positive
        if height < 0:
            height = 0
        if width < 0:
            width = 0

        # Evaluate these and get the path of the file where they are stored
        path = evaluator.evaluate(raw_text, width, height, X_RANGE, Y_RANGE)

    # Finally render the 'calculator.html' template substituting in raw_text
    # for the raw text on the form and path for the imate location
    return flask.render_template(
        'calculator.html',
        raw_text=raw_text,
        image_location=path)


# Not implemented
@app.route('/saved-graphs')
def saved_graphs():
    pass


# If running the file directly, host the flask server locally on the default
# port. It is currently in debug mode as that allows for easy debugging.
if __name__ == '__main__':
    app.run(host='localhost', port=PORT, debug=True)
