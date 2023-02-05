import evaluator.local


class ExecutionTree:
    def __init__(self):
        self.__root = None
        self.nodes = set()

    class __Node:
        def __init__(self):
            self.parent = None
            self.children = set()
            self.locals = None

        def set_locals(self, local_):
            self.locals = local_

        def get_var(self, identifier):
            return self.locals.get_var(identifier)

        def del_var(self, identifier):
            self.locals.del_var(identifier)

        def set_var(self, identifier, value):
            self.locals.set_var(identifier, value)

        def get_parent(self):
            return self.parent

        def add_child(self, child):
            if child is not None:
                self.children.add(child)
                child.set_parent(self)

        def remove_child(self, child):
            self.children.remove(child)
            child.set_parent(None)

        def set_parent(self, parent):
            self.parent = parent

        def __iter__(self):
            yield self

        def is_function_call(self):
            return False

        def is_identifier(self):
            return False

        def is_funcdef(self):
            return False

        def is_root(self):
            return self.parent is None

    class __Identifier(__Node):
        def __init__(self, name):
            self.name = name

            super().__init__()

        def __repr__(self):
            return f"{self.name}"

        def __iter__(self):
            yield self

        def is_identifier(self):
            return True

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

        def set_parameter(self, parameter):
            old_parameter = self.parameter
            if old_parameter is not None:
                self.remove_child(old_parameter)
                del old_parameter
            self.add_parameter(parameter)

        def set_function(self, function):
            old_function = self.function
            if old_function is not None:
                self.remove_child(old_function)
                del old_function
            self.add_function(function)

        def __repr__(self):
            return f"({self.function} {self.parameter})"

        def __iter__(self):
            yield self
            if self.function is not None:
                yield from self.function
            if self.parameter is not None:
                yield from self.parameter

        def is_function_call(self):
            return True

    class __FunctionDef(__Node):
        def __init__(self, identifier):
            self.identifier = identifier
            self.expr = None
            super().__init__()

        def set_expr(self, expr):
            self.expr = expr
            self.add_child(self.expr)

        def __repr__(self):
            return f"λ{self.identifier}.{self.expr}"

        def __iter__(self):
            yield self
            yield from self.expr

        def set_locals(self, locals_):
            super().set_locals(locals_)
            self.locals.set_var(self.identifier.name.item, None)

        def apply(self, value):
            self.locals.set_var(self.identifier.name.item, value)
            return self.expr

        def is_funcdef(self):
            return True

    def __set_root(self, root):
        self.__root = root

    def set_locals(self, globals_):
        for node in self.nodes:
            if node.is_root():
                node.set_locals(globals_)
            else:
                locals_ = evaluator.local.Locals()
                locals_.set_node(node)

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

    def create_function_def(self, identifier):
        node = ExecutionTree.__FunctionDef(identifier)
        self.nodes.add(node)
        return node


    def print_tree(self, node=None):
        print(self.__root)

    def __iter__(self):
        return iter(self.__root)


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