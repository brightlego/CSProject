import flask
import matplotlib.pyplot as plt
import numpy as np
import evaluator

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
    path = "static/test.png"
    height = 0
    width = 0
    if flask.request.method == 'POST':
        raw_text = flask.request.form.get('raw_text')
        parser = evaluator.parser.Parser(raw_text)
        execution_trees = parser.parse()
        executor = evaluator.executor.Executor(execution_trees)
        height = int(flask.request.cookies['height'])
        width = int(flask.request.cookies['width'])
        path = executor.graph(width, height, (-5, 5), (-5, 5))

    return flask.render_template('calculator.html', raw_text=raw_text, image_location=path)


@app.route('/saved-graphs')
def saved_graphs():
    pass


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
