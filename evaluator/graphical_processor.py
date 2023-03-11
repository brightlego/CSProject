import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
import evaluator.builtins.functions
import evaluator.builtins.types

DPI = 96


class Grapher:
    def __init__(self, executor, width, height):
        self.executor = executor
        self.width = width
        self.height = height
        self.xrange = (-5, 5)
        self.yrange = (-5, 5)

    def graph(self, xrange, yrange):
        evaluator.builtins.functions.executor = self.executor
        plt.figure(figsize=(self.width/DPI, self.height/DPI), dpi=DPI)

        error_message = ""

        self.xrange = xrange
        self.yrange = yrange
        for tree in self.executor.trees:
            try:
                if self.is_y_fx(tree):
                    function = self.get_function(tree)
                    self.y_fx(function)
                elif self.is_parametric(tree):
                    root = tree.get_root()
                    x_function = root.function.parameter
                    y_function = root.parameter
                    self.parametric(x_function, y_function, np.arange(-10, 10, 0.01))
                elif self.is_intersect(tree):
                    root = tree.get_root()
                    function1 = root.parameter.function.parameter
                    function2 = root.parameter.parameter
                    self.intersect(function1, function2)
                elif self.is_implicit(tree):
                    root = tree.get_root()
                    left_func = root.function.parameter
                    right_func = root.parameter
                    self.implicit(right_func, left_func)
            except Exception as err:
                error_message += f"Something went wrong when plotting statement {self.executor.trees.index(tree)+1}. "
        return self.plot(), error_message

    def plot(self):
        plt.xlim(self.xrange[0], self.xrange[1])
        plt.ylim(self.yrange[0], self.yrange[1])
        plt.grid(visible=True, which="both")
        plt.tight_layout()
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

    def is_implicit(self, tree):
        root = tree.get_root()
        if root.function.is_function_call():
            if root.function.function.is_identifier():
                if root.function.function.name.item == '=':
                    return True
        return False

    def implicit(self, right_func, left_func):
        xs = np.linspace(self.xrange[0], self.xrange[1], self.width//10)
        ys = np.linspace(self.yrange[0], self.yrange[1], self.height//10)
        X, Y = np.meshgrid(xs, ys)
        Z = np.zeros(X.shape)
        for i in range(self.width//10):
            for j in range(self.height//10):
                Z[j, i] = (self.executor.evaluate_function(right_func, (X[j, i], Y[j, i]), ('x', 'y')) -
                           self.executor.evaluate_function(left_func, (X[j, i], Y[j, i]), ('x', 'y')))

        border_points = [[],[]]

        dx = 0.000001

        for i in range(1, self.width//10-1):
            for j in range(1, self.height//10-1):
                if Z[j-1, i] < 0 < Z[j+1, i] or Z[j+1, i] < 0 < Z[j-1, i] or Z[j, i-1] < 0 < Z[j, i+1] or Z[j, i+1] < 0 < Z[j, i-1]:
                    x = X[j, i]
                    y = Y[j, i]

                    counter = 0
                    height = Z[j-1, i]
                    while height**2 > 0.00001 and counter < 50 :
                        height = self.executor.evaluate_function(right_func, (x, y),
                                                                 ('x', 'y')) - self.executor.evaluate_function(
                            left_func, (x, y), ('x', 'y'))
                        x_derivative = (height -
                                        self.executor.evaluate_function(right_func, (x - dx, y), ('x', 'y')) +
                                        self.executor.evaluate_function(left_func, (x - dx, y), ('x', 'y'))) / dx
                        x -= height/x_derivative
                        counter += 1

                    if counter < 50:
                        border_points[0].append(x)
                        border_points[1].append(y)

        verts = []
        codes = []

        for i in range(len(border_points[0])):
            for direction in [-1, 1]:
                x = border_points[0][i]
                y = border_points[1][i]

                verts.append((x, y))
                codes.append(Path.MOVETO)

                for _ in range(100):
                    height = self.executor.evaluate_function(right_func, (x, y),
                                                             ('x', 'y')) - self.executor.evaluate_function(
                        left_func, (x, y), ('x', 'y'))
                    x_derivative = (height -
                                    self.executor.evaluate_function(right_func, (x - dx, y), ('x', 'y')) +
                                    self.executor.evaluate_function(left_func, (x - dx, y), ('x', 'y'))) / dx
                    y_derivative = (height -
                                    self.executor.evaluate_function(right_func, (x, y - dx), ('x', 'y')) +
                                    self.executor.evaluate_function(left_func, (x, y - dx), ('x', 'y'))) / dx

                    x -= height/x_derivative
                    verts.append((x,y))
                    codes.append(Path.MOVETO)


                    normal = np.sqrt(x_derivative**2 + y_derivative**2)
                    normal *= direction
                    normal *= 100
                    x_derivative /= normal
                    y_derivative /= normal
                    x_derivative, y_derivative = -x_derivative, y_derivative
                    x += x_derivative
                    y += y_derivative

                    verts.append((x, y))
                    codes.append(Path.LINETO)

        path = Path(verts, codes)
        patch = patches.PathPatch(path)
        plt.gca().add_patch(patch)

    def is_parametric(self, tree):
        root = tree.get_root()
        if root.function.is_function_call():
            if root.function.function.is_identifier():
                if root.function.function.name.item == ',':
                    return True
        return False

    def parametric(self, x_function, y_function, t_values):
        x_values = []
        y_values = []
        for t in t_values:
            x_values.append(self.executor.evaluate_function(x_function, t, identifier='t'))
            y_values.append(self.executor.evaluate_function(y_function, t, identifier='t'))
        plt.plot(x_values, y_values)

    def is_intersect(self, tree):
        root = tree.get_root()
        if root.function.is_identifier():
            if root.function.name.item == 'intersect':
                if (root.parameter.is_function_call()
                    and root.parameter.function.is_function_call()
                    and root.parameter.function.function.is_identifier()
                    and root.parameter.function.function.name.item == ','):
                    return True
        return False

    def intersect(self, function1, function2):
        x = 0
        dx = 0.0001
        height = 1

        for _ in range(100):
            height = self.executor.evaluate_function(function1, x) - \
                     self.executor.evaluate_function(function2, x)
            slope = (height - self.executor.evaluate_function(function1, x - dx)
                     + self.executor.evaluate_function(function2, x - dx)) / dx
            x -= height/slope
        if height**2 < 0.001:
            y = self.executor.evaluate_function(function1, x)
            plt.scatter([x], [y])
            plt.gca().annotate(f"({x:f}, {y:f})", (x, y))

    def get_function(self, tree):
        root = tree.get_root()
        return root.parameter

