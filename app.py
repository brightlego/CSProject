import flask
import matplotlib.pyplot as plt
import numpy as np

app = flask.Flask(__name__)


@app.route('/')
def root():
    return flask.redirect('/calculator')


@app.route('/login')
def login():
    return flask.render_template('login.html')


@app.route('/signup')
def signup():
    return flask.render_template('signup.html')


@app.route('/calculator')
def calculator():
    return flask.render_template('calculator.html', raw_text="", image_location="test.png")


@app.route('/saved-graphs')
def saved_graphs():
    pass


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
