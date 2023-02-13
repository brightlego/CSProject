"""This file tests if all the external modules were installed correctly.

It has been left in so that it can be used to quickly test again if something
has happened.
"""

# Try to import the modules
import flask
import matplotlib.pyplot as plt
import numpy as np
import sqlite3

# Try to host a flask server
app = flask.Flask(__name__)


@app.route('/')
def test():

    # Try to plot a graph using matplotlib and numpy
    x = np.arange(0, 10, 0.1)
    y = x**2
    plt.plot(x, y)
    plt.savefig("static/test.png")

    # Show just the image produced
    return '<img src = "/static/test.png">'


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
