import re

NON_ALPHA_IDENTIFIERS = ''
BRACKETS = '()[]{}'


class Parser:
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
                if char.isalnum() or char in NON_ALPHA_IDENTIFIERS:
                    self.__curr_token += char
                else:
                    self.__add_token()
                    self.__curr_token += char  # As this is not whitespace, the char should be acknowledged
                    in_identifier = False

            elif char.isalpha():  # Single letter identifier
                self.__add_token()
                self.__curr_token += char
                in_whitespace = False

            elif char.isnumeric() or char == '.':
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

    def __add_token(self):
        if self.__curr_token:
            self.tokens.append(self.__curr_token)
            self.__curr_token = ""

    def __maintains_tokens_numericness(self, char):
        if re.fullmatch(
                r"([0-9]+|[0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([eE]-?[0-9]+)?",
                self.__curr_token + char):
            return True
        else:
            return False


def test():
    parser = Parser(r"\Sum(\alpha\beta\gamma) δ")
    parser.tokenise()
    print(parser.tokens)

if __name__ == '__main__':
    test()