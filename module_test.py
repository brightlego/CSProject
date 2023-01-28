import flask
import matplotlib.pyplot as plt
import numpy as np

app = flask.Flask(__name__)


@app.route('/')
def test():
    x = np.arange(0, 10, 0.1)
    y = x**2
    plt.plot(x, y)
    plt.savefig("static/test.png")
    return '<img src = "/static/test.png">'


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
