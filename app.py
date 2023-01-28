import flask
import matplotlib.pyplot as plt
import numpy as np

app = flask.Flask(__name__)

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
