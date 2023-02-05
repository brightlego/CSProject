import re
import evaluator.operators
import evaluator.execution_tree


class Parser:
    class __Token:
        def __init__(self, item):
            self.item = item

        def __repr__(self):
            return repr(self.item)

        def __str__(self):
            return str(self.item)

    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.tokens = []
        self.lines = []
        self.__curr_token = ""
        self.trees = []

    def parse(self):
        self.__tokenise()
        self.__negate()
        self.__break_lines()
        self.__reformat()
        self.__create_expression_tree()
        self.__equality_to_definition()
        self.__function_definition_to_lambda()
        [i.print_tree() for i in self.trees]
        self.__lambda_expr_to_def_node()
        [i.print_tree() for i in self.trees]
        return self.trees

    def __tokenise(self):
        self.__curr_token = ""
        in_whitespace = True
        in_number = False
        in_identifier = False

        for char in self.raw_text:
            if char == '\\':
                if in_identifier:
                    self.__curr_token = r"\\"
                    self.__add_token()
                    in_identifier = False
                    in_whitespace = True
                    in_number = False
                else:
                    self.__add_token()
                    in_identifier = True
                    in_whitespace = False
                    in_number = False

            elif char.isspace():
                if in_whitespace:
                    continue
                self.__add_token()
                in_identifier = False
                in_whitespace = True
                in_number = False

            elif in_number:
                if self.__maintains_tokens_numericness(char) or self.__maintains_tokens_numericness(char + '0'):
                    self.__curr_token += char
                else:
                    if self.__curr_token[-1] in 'eE':
                        suffix = self.__curr_token[-1]
                        self.__curr_token = self.__curr_token[:-1]
                        self.__add_token()
                        self.__curr_token = suffix
                    self.__add_token()
                    self.__curr_token += char  # As this is not whitespace, the char should be acknowledged
                    in_number = False

            elif in_identifier:
                if char.isalnum() or char in evaluator.operators.NON_ALPHA_IDENTIFIERS:
                    self.__curr_token += char
                else:
                    self.__add_token()
                    self.__curr_token += char  # As this is not whitespace, the char should be acknowledged
                    in_identifier = False

            elif char.isalpha():  # Single letter identifier
                self.__add_token()
                self.__curr_token += char
                in_whitespace = False

            elif char.isnumeric() or char in '.':
                self.__add_token()
                self.__curr_token += char
                in_whitespace = False
                in_number = True

            else:  # Otherwise, treat it as a single operator
                self.__add_token()
                self.__curr_token += char
                self.__add_token()
                in_whitespace = False

        self.__add_token()

        # This makes sure that arrows/le/ge/ne are treated as a single string
        new_tokens = []
        for i in self.tokens:
            if len(new_tokens) == 0:
                new_tokens.append(i)
            else:
                if (new_tokens[-1], i.item) in [('=', '>'), ('<', '='), ('>', '='), ('-', '>'), ('!', '=')]:
                    new_tokens[-1].item += i.item
                else:
                    new_tokens.append(i)

        self.tokens = new_tokens

    def __add_token(self):
        if self.__curr_token:
            self.tokens.append(self.__Token(self.__curr_token))
            self.__curr_token = ""

    @staticmethod
    def __is_number(string):
        if re.fullmatch(evaluator.operators.VALID_NUMBER_REGEX, string):
            return True
        else:
            return False

    def __maintains_tokens_numericness(self, char):
        if self.__is_number(self.__curr_token + char):
            return True
        else:
            return False

    @staticmethod
    def __get_operator_queue(tokens):
        queue = PriorityQueue()
        bracket_level = 0
        for i in range(len(tokens)):
            token = tokens[i].item
            score = (bracket_level, -1, -i)

            if token in evaluator.operators.START_BRACKETS:
                bracket_level += 1
            elif token in evaluator.operators.END_BRACKETS:
                bracket_level -= 1
            elif token in evaluator.operators.INFIX_BINARY_SCORE:
                score = (bracket_level, evaluator.operators.INFIX_BINARY_SCORE[token], -i)
            elif token in evaluator.operators.POSTFIX_UNARY_SCORE:
                score = (bracket_level, evaluator.operators.POSTFIX_UNARY_SCORE[token], -i)
            elif token in evaluator.operators.PREFIX_UNARY_SCORE:
                score = (bracket_level, evaluator.operators.PREFIX_UNARY_SCORE[token], -i)
            else:
                score = (bracket_level, 0, -i)

            queue.insert(tokens[i], score)
        return queue

    def __negate(self):
        for i in range(len(self.tokens)):
            if (i == 0
                    or self.tokens[i - 1].item in evaluator.operators.START_BRACKETS
                    or self.tokens[i - 1].item in evaluator.operators.OPERATORS
                    or self.tokens[i - 1].item in evaluator.operators.LINE_BREAK):
                if self.tokens[i].item == '-':
                    self.tokens[i].item = 'negate'
                elif self.tokens[i].item == '+':
                    self.tokens[i].item = 'ignore'

    def __break_lines(self):
        self.lines = [[]]
        for token in self.tokens:
            if token.item in evaluator.operators.LINE_BREAK:
                self.lines.append([])
            else:
                self.lines[-1].append(token)

    @staticmethod
    def __get_preblock(index, tokens):
        pre_block_index = index - 1
        bracket_level = 0
        while (bracket_level > 0 or (
                tokens[pre_block_index].item not in evaluator.operators.INFIX_BINARY_SCORE
                and tokens[pre_block_index].item not in evaluator.operators.START_BRACKETS)
        ):
            if tokens[pre_block_index].item in evaluator.operators.END_BRACKETS:
                bracket_level += 1
            elif tokens[pre_block_index].item in evaluator.operators.START_BRACKETS:
                bracket_level -= 1
            pre_block_index -= 1

        pre_block_index += 1

        return pre_block_index

    @staticmethod
    def __get_postblock(index, tokens):
        bracket_level = 0
        post_block_index = index + 1
        while (bracket_level > 0 or (
                tokens[post_block_index].item not in evaluator.operators.INFIX_BINARY_SCORE
                and tokens[post_block_index].item not in evaluator.operators.END_BRACKETS)
        ):
            if tokens[post_block_index].item in evaluator.operators.END_BRACKETS:
                bracket_level -= 1
            elif tokens[post_block_index].item in evaluator.operators.START_BRACKETS:
                bracket_level += 1
            post_block_index += 1

        return post_block_index

    def __reformat(self):
        for tokens in self.lines:
            queue = self.__get_operator_queue(tokens)
            tokens.insert(0, self.__Token('('))
            tokens.append(self.__Token(')'))
            while not queue.is_empty():
                token = queue.extract_max()
                index = tokens.index(token)
                if token.item in evaluator.operators.INFIX_BINARY_SCORE:
                    pre_block_index = self.__get_preblock(index, tokens)
                    post_block_index = self.__get_postblock(index, tokens)

                    tokens[index] = self.__Token(')')  # End of partial application
                    tokens.insert(post_block_index, self.__Token(')'))  # End of full application

                    tokens.insert(pre_block_index, token)
                    tokens.insert(pre_block_index, self.__Token('('))  # Start of partial application
                    tokens.insert(pre_block_index, self.__Token('('))  # Start of full application
                elif token.item in evaluator.operators.POSTFIX_UNARY_SCORE:
                    pre_block_index = self.__get_preblock(index, tokens)
                    tokens.insert(index, self.__Token(')'))  # Application end

                    tokens.insert(pre_block_index, token)
                    tokens.insert(pre_block_index, self.__Token('('))  # Application start
                elif token.item not in evaluator.operators.BRACKETS:
                    post_block_index = self.__get_postblock(index, tokens)
                    tokens.insert(post_block_index, self.__Token(')'))  # End of application
                    tokens.insert(index, self.__Token('('))  # Start of application

    def __create_expression_tree(self):
        for tokens in self.lines:
            tree = evaluator.execution_tree.ExecutionTree()
            root = tree.create_function_call()
            assert root is tree.get_root()
            self.__recurse_create_tree(tree, root, iter(tokens))
            self.__compress_tree(tree)
            self.trees.append(tree)

    def __recurse_create_tree(self, tree, parent, iterator):
        children = []
        for token in iterator:
            if token.item in evaluator.operators.START_BRACKETS:
                child = tree.create_function_call()
                self.__recurse_create_tree(tree, child, iterator)
                children.append(child)
            elif token.item in evaluator.operators.END_BRACKETS:
                break
            else:
                child = tree.create_identifier(token)
                children.append(child)
        match len(children):
            case 0:
                raise ValueError('Empty brackets')
            case 1:
                parent.add_parameter(children[0])
            case 2:
                parent.add_function(children[0])
                parent.add_parameter(children[1])
            case n:
                function = children[0]
                parameter = children[1]
                for i in range(2, n):
                    node = tree.create_function_call()
                    node.add_function(function)
                    node.add_parameter(parameter)
                    function = node
                    parameter = children[i]
                parent.add_function(function)
                parent.add_parameter(parameter)

    @staticmethod
    def __compress_tree(tree):
        for node in tree:
            if node.is_function_call():
                while node.parameter.is_function_call() and node.parameter.function is None:
                    node.set_parameter(node.parameter.parameter)
                while node.function is not None and node.function.is_function_call() and node.function.function is None:
                    node.set_function(node.function.parameter)
        root = tree.get_root()
        if root.function is None:
            root.set_function(root.parameter.function)
            root.set_parameter(root.parameter.parameter)

    def __equality_to_definition(self):
        for tree in self.trees:
            root = tree.get_root()
            if (root.function.is_function_call()
                    and root.function.function.is_identifier()
                    and root.function.function.name.item == '='):
                if (root.function.parameter.is_function_call()
                        and root.function.parameter.function.is_identifier()
                        and root.function.parameter.function.name.item == 'let'):
                    root.set_function(root.function.parameter)

    def __function_definition_to_lambda(self):
        for tree in self.trees:
            root = tree.get_root()
            if (root.function.is_function_call()
                    and root.function.function.is_identifier()
                    and root.function.function.name.item == 'let'):
                if root.function.parameter.is_function_call():
                    node = root.function.parameter
                    while node.is_function_call():
                        lambda_expr = tree.create_function_call()
                        lambda_ = tree.create_identifier(self.__Token('lambda'))
                        value = node.parameter

                        lambda_expr.add_function(lambda_)
                        lambda_expr.add_parameter(value)

                        parent_call = tree.create_function_call()
                        parent_call.add_function(lambda_expr)
                        parent_call.add_parameter(root.parameter)

                        root.set_parameter(parent_call)
                        node = node.function

                    root.function.set_parameter(node)

    def __lambda_expr_to_def_node(self):
        for tree in self.trees:
            for node in tree:
                if node.is_function_call():
                    if node.function.is_function_call():
                        if node.function.function.is_identifier():
                            if node.function.function.name.item == 'lambda':
                                function_def = tree.create_function_def(node.function.parameter)
                                function_def.set_expr(node.parameter)
                                if node.parent.is_function_call():
                                    if node.parent.function is node:
                                        node.parent.add_function(function_def)
                                    else:
                                        node.parent.add_parameter(function_def)
                                elif node.is_root():
                                    tree.set_root(function_def)
                                else:
                                    node.parent.set_expr(function_def)

class PriorityQueue:
    def __init__(self):
        self.__heap = [(-1, None)]  # Heaps are best implemented using 1-indexed arrays
        self.n = 0

    def insert(self, item, priority):
        self.__heap.append((priority, item))
        self.n += 1
        i = self.n
        while i > 1 and self.__heap[i >> 1][0] < self.__heap[i][0]:
            swap(self.__heap, i, i >> 1)
            i >>= 1

    def extract_max(self):
        if self.n <= 0:
            return None
        else:
            value = self.__heap[1][1]
            self.__heap[1] = self.__heap[self.n]
            del self.__heap[self.n]
            self.n -= 1
            i = 1
            while (i << 1) | 1 <= self.n and (self.__heap[i][0] < self.__heap[i << 1][0]
                                              or self.__heap[i][0] < self.__heap[(i << 1) | 1][0]):
                if self.__heap[i << 1][0] > self.__heap[(i << 1) | 1][0]:
                    swap(self.__heap, i, i << 1)
                    i <<= 1
                else:
                    swap(self.__heap, i, (i << 1) | 1)
                    i <<= 1
                    i |= 1

        return value

    def debug_print(self):
        print(self.__heap)

    def is_empty(self):
        return self.n <= 0

    def __len__(self):
        return self.n


def test():
    parser = Parser(r"""\let f(x) = 2 + ((\lambda x) (x^2))(5)""")
    trees = parser.parse()


def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


if __name__ == '__main__':
    test()
