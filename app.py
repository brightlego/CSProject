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


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    raw_text = ""
    print(flask.request.method)
    if flask.request.method == 'POST':
        raw_text = flask.request.form.get('raw_text')
        print(raw_text)

    return flask.render_template('calculator.html', raw_text=f"'{raw_text}' was received", image_location="test.png")


@app.route('/saved-graphs')
def saved_graphs():
    pass


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
