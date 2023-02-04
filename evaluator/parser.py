import re
import builtin_operators


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
        self.__curr_token = ""

    def tokenise(self):
        self.__curr_token = ""
        in_whitespace = True
        in_number = False
        in_identifier = False

        for char in self.raw_text:
            if char == '\\':
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
                if char.isalnum() or char in builtin_operators.NON_ALPHA_IDENTIFIERS:
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
        if re.fullmatch(
                r"-?([0-9]+|[0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([eE]-?[0-9]+)?",
                string):
            return True
        else:
            return False

    def __maintains_tokens_numericness(self, char):
        if self.__is_number(self.__curr_token + char):
            return True
        else:
            return False


    def __get_operator_queue(self):
        queue = PriorityQueue()
        bracket_level = 0
        for i in range(len(self.tokens)):
            token = self.tokens[i].item
            score = (bracket_level, -1, -i)

            if token in builtin_operators.START_BRACKETS:
                bracket_level += 1
            elif token in builtin_operators.END_BRACKETS:
                bracket_level -= 1
            elif token in builtin_operators.INFIX_BINARY_SCORE:
                score = (bracket_level, builtin_operators.INFIX_BINARY_SCORE[token], -i)
            elif token in builtin_operators.POSTFIX_UNARY_SCORE:
                score = (bracket_level, builtin_operators.POSTFIX_UNARY_SCORE[token], -i)
            elif token in builtin_operators.PREFIX_UNARY_SCORE:
                score = (bracket_level, builtin_operators.PREFIX_UNARY_SCORE[token], -i)
            else:
                score = (bracket_level, 0, -i)

            queue.insert(self.tokens[i], score)
        return queue

    def reformat(self):
        queue = self.__get_operator_queue()
        self.tokens.insert(0, self.__Token('('))
        self.tokens.append(self.__Token(')'))
        while not queue.is_empty():
            token = queue.extract_max()
            index = self.tokens.index(token)
            if token.item in builtin_operators.INFIX_BINARY_SCORE:
                pre_block_index = index - 1
                bracket_level = 0
                while (bracket_level > 0 or (
                        self.tokens[pre_block_index].item not in builtin_operators.INFIX_BINARY_SCORE
                        and self.tokens[pre_block_index].item not in builtin_operators.START_BRACKETS)
                ):
                    if self.tokens[pre_block_index].item in builtin_operators.END_BRACKETS:
                        bracket_level += 1
                    elif self.tokens[pre_block_index].item in builtin_operators.START_BRACKETS:
                        bracket_level -= 1
                    pre_block_index -= 1

                pre_block_index += 1

                bracket_level = 0
                post_block_index = index + 1
                while (bracket_level > 0 or (
                        self.tokens[post_block_index].item not in builtin_operators.INFIX_BINARY_SCORE
                        and self.tokens[post_block_index].item not in builtin_operators.END_BRACKETS)
                ):
                    if self.tokens[post_block_index].item in builtin_operators.END_BRACKETS:
                        bracket_level -= 1
                    elif self.tokens[post_block_index].item in builtin_operators.START_BRACKETS:
                        bracket_level += 1
                    post_block_index += 1

                self.tokens[index] = self.__Token(')')   # End of partial application

                self.tokens.insert(post_block_index, self.__Token(')'))  # End of post-block
                self.tokens.insert(post_block_index, self.__Token(')'))  # End of full application

                self.tokens.insert(index + 1, self.__Token('('))  # Start of post-block
                self.tokens.insert(index, self.__Token(')'))  # End of pre-block

                self.tokens.insert(pre_block_index,  self.__Token('('))  # Bracket for pre-block
                self.tokens.insert(pre_block_index, token)
                self.tokens.insert(pre_block_index,  self.__Token('('))  # Bracket for partial application
                self.tokens.insert(pre_block_index,  self.__Token('('))  # Bracket for full application




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
            while (i<<1)|1 <= self.n and (self.__heap[i][0] < self.__heap[i<<1][0]
                                          or self.__heap[i][0] < self.__heap[(i<<1)|1][0]):
                if self.__heap[i<<1][0] > self.__heap[(i<<1)|1][0]:
                    swap(self.__heap, i, i<<1)
                    i <<= 1
                else:
                    swap(self.__heap, i, (i<<1)|1)
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
    parser = Parser(r"""\sin(90) + \exp(5) + 3^2""")
    parser.tokenise()
    print(parser.tokens)
    parser.reformat()
    print(parser.tokens)


def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


if __name__ == '__main__':
    test()
