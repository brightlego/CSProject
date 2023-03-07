"""The parser to parse raw text into execution trees

Classes:
    Parser(object)
        -- The parser class that is used to parse text into execution trees
    PriorityQueue(object)
        -- A priority queue implemented using a heap

Functions:
    test() -> None
        -- Used to test if the parser is working
    swap(arr: list, i: int, j: int) -> None
        -- Swaps two items in an array

"""

# For checking if something is a number
import re

# Importing the internal modules
import evaluator.operators
import evaluator.execution_tree


class Parser:
    """The parser class used to parse text into expression trees

    Classes:
        Parser.__Token(object)
            -- The class which is used to make tokens unique

    Attributes:
        __raw_text: str
            -- The raw text that is yet to be parsed
        __tokens: list[Parser.__Token] (default [])
            -- The tokens that have been parsed
        __lines: list[list[Parser.__Token]] (default [])
            -- The tokens after they have been split into multiple lines
        __curr_token: str (default "")
            -- The current token in the process of being tokenised
        __trees: list[evaluator.execution_tree.ExecutionTree]
            -- The parsed trees for each line

    Methods:
        __init__(raw_text: str)
            -- The initiliser for the class

        parse() -> list[evaluator.execution_tree.ExecutionTree]
            -- Parses the statements and returns the parsed trees for each line

        __tokenise() -> None
            -- Tokenises the raw text and puts the tokens into __tokens

        __add_token() -> None
            -- Adds the current token into __tokens

        __is_number(string: str) -> bool
            -- Checks if the string is a valid number

        __maintains_tokens_numericness(char: str) -> bool
            -- Checks if adding char onto the end of the token keeps it a
               valid number

        __get_operator_queue(tokens: list[Parser.__Tokens]) -> PriorityQueue
            -- Returns a queue of all the tokens in order of when to re-arange
               them

        __negate() -> None
            -- Converts the subtraction/addition operators into negation/ignore
               operators in the right conditions resepctively.

        __break_lines() -> None
            -- Breaks __tokens up into separate lines and puts them in __lines

        __get_preblock(index: int, tokens: list[Parser.__Token]) -> int
            -- Gets the index of the start of the preceding block

        __get_postblock(index: int, tokens: list[Parser.__Token]) -> int
            -- Gets the index of the end of the succeeding block

        __reformat() -> None
            -- Reformats the tokens into prefix notation

        __create_expression_trees() -> None
            -- Creates the expression trees from the lines of tokens

        __recurse_create_tree(
                tree: evaluator.expression_tree.ExpressionTree
                parent: evaluator.expression_tree.ExpressionTree.__Node
                iterator: Iterator)
            -- Creates the expression tree using a recursive algorithm

        __compress_tree() -> None
            -- Makes sure that every node in the tree has either 2 children or
               is a leaf.

        __equality_to_definition() -> None
            -- Converts Statements in the form ((= (let ...)) ...) into the
               form ((let ...) ...)

        __function_definition_to_lambda() -> None
            -- Converts defining a function into assigning a lambda expression

        __lambda_expr_to_def_node() -> None
            -- Converts a lambda expression into a node defining an anonymous
               function
    """
    class __Token:
        """The class which is used to make tokens unique

        Attributes:
            item: str
                -- The token stored

        Methods:
            __init__(item: str)
                -- The initiliser
            __repr__() -> str
                -- Used for the debug representation of the class
            __str__() -> str
                -- Used for the string representation of the class
        """
        def __init__(self, item):
            """The initiliser

            Arguments:
                item: str
                    -- The item stored
            """
            self.item = item

        def __repr__(self):
            """Used for the debug representation of the class

            Arguments:
                None

            Returns:
                representation: str
                    -- The debug representation of the item
            """
            return repr(self.item)

        def __str__(self):
            """Used for the string representation of the class
            Arguments:
                None

            Returns:
                representation: str
                    -- The string representation of the item
            """
            return str(self.item)

    def __init__(self, raw_text):
        """The initiliser for the class

        Arguments:
            raw_text: str
                -- The raw text to be parsed
        """
        self.__raw_text = raw_text
        self.__tokens = []
        self.__lines = []
        self.__curr_token = ""
        self.__trees = []

    def parse(self):
        """Parses the statements and returns the parsed trees for each line

        Executes the necessary functions to parse the trees in order.

        Arguments:
            None

        Returns:
            trees: list[evaluator.execution_tree.ExecutionTree]
        """

        # The order is self-explanatory
        self.__tokenise()
        self.__negate()
        self.__break_lines()
        self.__reformat()
        self.__create_expression_trees()
        self.__equality_to_definition()
        self.__function_definition_to_lambda()
        self.__lambda_expr_to_def_node()
        return self.__trees

    def __tokenise(self):
        """Tokenises the raw text and puts the tokens into __tokens

        Arguments:
            None

        Returns:
            None
        """

        self.__curr_token = ""  # Resets the current token

        # The pointer is treated as initially in whitespace as that indicates
        # that the tokeniser should look out for the next item and ignore any
        # initial whitepace.
        in_whitespace = True  # Is the pointer currently in whitespace?
        in_number = False  # Is the pointer currently in a literal number?
        in_identifier = False  # Is the pointer currently in an identifier?

        # Iterate through __raw_text characterwise
        for char in self.__raw_text:

            # If the character is a '\', it is either the start of an
            # identifier, or the end of a line break
            if char == '\\':
                # If
                if in_identifier and self.__curr_token == "":
                    self.__curr_token = "\\\\"
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
                if (self.__maintains_tokens_numericness(char)
                        or self.__maintains_tokens_numericness(char + '0')):
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
        for i in self.__tokens:
            if len(new_tokens) == 0:
                new_tokens.append(i)
            else:
                if (new_tokens[-1], i.item) in [('=', '>'), ('<', '='), ('>', '='), ('-', '>'), ('!', '=')]:
                    new_tokens[-1].item += i.item
                else:
                    new_tokens.append(i)

        self.__tokens = new_tokens

    def __add_token(self):
        if self.__curr_token:
            self.__tokens.append(self.__Token(self.__curr_token))
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
        for i in range(len(self.__tokens)):
            if (i == 0
                    or self.__tokens[i - 1].item in evaluator.operators.START_BRACKETS
                    or self.__tokens[i - 1].item in evaluator.operators.OPERATORS
                    or self.__tokens[i - 1].item in evaluator.operators.LINE_BREAK):
                if self.__tokens[i].item == '-':
                    self.__tokens[i].item = 'negate'
                elif self.__tokens[i].item == '+':
                    self.__tokens[i].item = 'ignore'

    def __break_lines(self):
        self.__lines = [[]]
        for token in self.__tokens:
            if token.item in evaluator.operators.LINE_BREAK:
                self.__lines.append([])
            else:
                self.__lines[-1].append(token)

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

    # noinspection PyUnresolvedReferences
    def __reformat(self):
        for tokens in self.__lines:
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

    def __create_expression_trees(self):
        for tokens in self.__lines:
            tree = evaluator.execution_tree.ExecutionTree()
            root = tree.create_function_call()
            assert root is tree.get_root()
            self.__recurse_create_tree(tree, root, iter(tokens))
            self.__compress_tree(tree)
            self.__trees.append(tree)

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
        for tree in self.__trees:
            root = tree.get_root()
            if (root.function.is_function_call()
                    and root.function.function.is_identifier()
                    and root.function.function.name.item == '='):
                if (root.function.parameter.is_function_call()
                        and root.function.parameter.function.is_identifier()
                        and root.function.parameter.function.name.item == 'let'):
                    root.set_function(root.function.parameter)

    def __function_definition_to_lambda(self):
        for tree in self.__trees:
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
        for tree in self.__trees:
            for node in tree:
                if node.is_function_call():
                    if node.function.is_function_call():
                        if node.function.function.is_identifier():
                            if node.function.function.name.item == 'lambda':
                                function_def = tree.create_function_def(
                                    node.function.parameter)
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
        # Heaps are best implemented using 1-indexed arrays
        self.__heap = [(-1, None)]
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
