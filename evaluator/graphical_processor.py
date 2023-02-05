import matplotlib.pyplot as plt
import numpy as np

DPI = 96

class Grapher:
    def __init__(self, executor, width, height):
        self.executor = executor
        self.width = width
        self.height = height
        self.xrange = (-5, 5)
        self.yrange = (-5, 5)

    def graph(self, xrange, yrange):
        plt.figure(figsize=(self.width/DPI, self.height/DPI), dpi=DPI)
        self.xrange = xrange
        self.yrange = yrange
        for tree in self.executor.trees:
            if self.is_y_fx(tree):
                function = self.get_function(tree)
                self.y_fx(function)
        return self.plot()

    def plot(self):
        plt.xlim(self.xrange[0], self.xrange[1])
        plt.ylim(self.yrange[0], self.yrange[1])
        name = ''.join([hex(i)[2:] for i in np.random.bytes(4)])
        name += '.png'
        name = 'static/images/' + name
        plt.savefig('./'+name, dpi=DPI)
        return name

    def y_fx(self, function):
        x_values = np.linspace(self.xrange[0], self.xrange[1], self.width)
        y_values = []
        for x in x_values:
            y_values.append(self.executor.evaluate_function(function, x))
        plt.plot(x_values, y_values)

    def is_y_fx(self, tree):
        root = tree.get_root()
        if root.parameter.is_funcdef():
            return True
        elif root.function.is_function_call():
            if root.function.function.is_identifier() and root.function.parameter.is_identifier():
                if root.function.function.name.item == '=' and root.function.parameter.name.item == 'y':
                    return True
        return False

    def get_function(self, tree):
        root = tree.get_root()
        if root.parameter.is_funcdef():
            return root.parameter
        else:
            return root.parameter

