import evaluator.operators
import evaluator.builtins.functions
import evaluator.builtins.types
import evaluator.local
import evaluator.graphical_processor
import re

class Executor:
    def __init__(self, trees):
        self.trees = trees
        self.globals = evaluator.local.Globals()

        for tree in self.trees:
            tree.set_locals(self.globals)

        for operator in evaluator.builtins.functions.OPERATORS:
            self.globals.set_var(operator, evaluator.builtins.functions.OPERATORS[operator])

        self.set_globals()
        self.grapher = None

    def graph(self, width, height, xrange, yrange):
        self.grapher = evaluator.graphical_processor.Grapher(self, width, height)
        return self.grapher.graph(xrange, yrange)

    def set_globals(self):
        for tree in self.trees:
            root = tree.get_root()
            if root.function.is_function_call():
                if root.function.function.is_identifier():
                    if root.function.function.name.item == 'let':
                        assert root.function.parameter.is_identifier()
                        identifier = root.function.parameter.name.item
                        self.globals.set_var(identifier, root.parameter)

    def evaluate_tree(self, tree):
        root = tree.get_root()
        return self.__evaluate_node(root)

    def evaluate_function(self, node, value, identifier='x'):
        if isinstance(value, float) or isinstance(value, int):
            parameter = evaluator.builtins.types.Number(value)

            if not isinstance(node, evaluator.builtins.types.Function):
                if node.is_funcdef():
                    result = self.__evaluate_node(node.apply(parameter))
                    if isinstance(result, evaluator.builtins.types.Number):
                        return result.value
                    else:
                        raise ValueError
                else:
                    node.set_var(identifier, parameter)
                    out = self.__evaluate_node(node)
                    node.del_var(identifier)
                    if isinstance(out, evaluator.builtins.types.Number):
                        return out.value
                    else:
                        raise ValueError
            result = node.apply(parameter)
            if isinstance(result, evaluator.builtins.types.Number):
                return result.value
            else:
                raise ValueError
        if isinstance(value, tuple):
            if len(value) != len(identifier):
                raise ValueError
            for v, i in zip(value, identifier):
                if not (isinstance(v, float) or isinstance(v, int)):
                    raise ValueError
                node.set_var(i, evaluator.builtins.types.Number(v))
            out = self.__evaluate_node(node)
            for i in identifier:
                node.del_var(i)
            if isinstance(out, evaluator.builtins.types.Number):
                return out.value
            else:
                return out
        else:
            raise ValueError

    def __evaluate_node(self, node):
        if node.is_function_call():
            function = self.__evaluate_node(node.function)

            if not isinstance(function, evaluator.builtins.types.Function) \
                    and function.is_identifier():
                if function.name.item == '"':
                    if node.parameter.is_identifier():
                        return evaluator.builtins.types.IdentifierName(
                            node.parameter.name)
                    else:
                        raise ValueError

            parameter = self.__evaluate_node(node.parameter)

            if not isinstance(function, evaluator.builtins.types.Function) \
                    and function.is_funcdef():
                return self.__evaluate_node(function.apply(parameter))
            try:
                return function.apply(parameter)
            except ValueError:
                return node

        elif node.is_identifier():
            if re.fullmatch(evaluator.operators.VALID_NUMBER_REGEX,
                            node.name.item):
                return evaluator.builtins.types.Number(float(node.name.item))
            else:
                value = node.get_var(node.name.item)
                if isinstance(value, evaluator.builtins.types.Function):
                    return value
                elif value is None:
                    return node
                else:
                    return self.__evaluate_node(value)
        else:
            return node


if __name__ == '__main__':
    import parser
    parser = parser.Parser(r"\let f(x) = 1 + x")
    trees = parser.parse()
    executor = Executor(trees)
    executor.graph(800, 800, (-5, 5), (-5, 5))