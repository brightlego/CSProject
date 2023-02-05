class Locals:
    def __init__(self, node):
        self.vars = {}
        self.node = node

    def get_var(self, identifier):
        if identifier in self.vars:
            return self.vars[identifier]
        else:
            if not self.node.is_root():
                return self.node.get_parent().get_var(identifier)

    def set_node(self, node):
        self.node = node
        node.set_locals(self)

    def set_var(self, identifier, value=None):
        self.vars[identifier] = value


class Globals(Locals):
    def get_var(self, identifier):
        if identifier in self.vars:
            return self.vars[identifier]
        else:
            return None
