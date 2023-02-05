import operators
import execution_tree
import evaluator.builtins.functions
import evaluator.builtins.types
import local

class Executor:
    def __init__(self, trees):
        self.trees = trees
        self.globals = local.Globals()

        for tree in self.trees:
            tree.add_locals(self.globals)

        for operator in evaluator.builtins.functions.OPERATORS:
            self.globals.set_var(operator, evaluator.builtins.functions.OPERATORS[operator])
