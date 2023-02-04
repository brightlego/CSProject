from typing import Union


class ExecutionTree:
    def __init__(self):
        self.__root = None
        self.nodes = set()

    class __Node:
        def __init__(self):
            self.parent = None
            self.children = set()

        def add_child(self, child):
            self.children.add(child)
            child.set_parent(self)

        def set_parent(self, parent):
            self.parent = parent

    class __Identifier(__Node):
        def __init__(self, name):
            self.name = name

            super().__init__()

    class __FunctionCall(__Node):
        def __init__(self):
            self.function = None
            self.parameter = None

            super().__init__()

        def add_function(self, function):
            self.function = function
            self.add_child(function)

        def add_parameter(self, parameter):
            self.parameter = parameter
            self.add_child(parameter)

    def __set_root(self, root):
        self.__root = root

    def get_root(self):
        return self.__root

    def create_identifier(self, name):
        node = ExecutionTree.__Identifier(name)
        self.nodes.add(node)
        if self.__root is None:
            self.__set_root(node)
        return node

    def create_function_call(self):
        node = ExecutionTree.__FunctionCall()
        self.nodes.add(node)
        if self.__root is None:
            self.__set_root(node)
        return node

    def print_tree(self, node=None):
        if node is None:
            node = self.__root

        if isinstance(node, ExecutionTree.__FunctionCall):
            print('(', end='')
            if isinstance(node.function, ExecutionTree.__Identifier):
                print('(', end='')
            self.print_tree(node.function)
            self.print_tree(node.parameter)
        else:
            print(f"{node.name}) ", end='')

        if node is self.__root:
            print("\b)")


def test():
    tree = ExecutionTree()
    node = tree.create_function_call()
    ab = tree.create_function_call()
    cd = tree.create_function_call()
    a = tree.create_identifier('a')
    b = tree.create_identifier('b')
    c = tree.create_identifier('c')
    d = tree.create_identifier('d')
    ab.add_function(a)
    ab.add_parameter(b)
    cd.add_function(c)
    cd.add_parameter(d)
    node.add_function(ab)
    node.add_parameter(cd)
    tree.print_tree()


if __name__ == '__main__':
    test()