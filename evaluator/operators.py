INFIX_BINARY_SCORE = {'=': 0.5, '<': 1, '>': 1, '<=': 1, '>=': 1, '!=': 1, '=>': 2, '->': 2, '+': 10, '-': 10, '*': 20,
                      '/': 20, '^': 30, '_': 1000, '.': 1100, ',': 0}

POSTFIX_UNARY_SCORE = {'!': 40, "'": 40}

PREFIX_UNARY_SCORE = {'negate': 100, 'ignore': 110}

BLOCK_SCORE = 5

OPERATORS = list(INFIX_BINARY_SCORE.keys()) + list(POSTFIX_UNARY_SCORE.keys()) + list(PREFIX_UNARY_SCORE.keys())

NON_ALPHA_IDENTIFIERS = ''
START_BRACKETS = '([{'
END_BRACKETS = ')]}'
BRACKETS = START_BRACKETS + END_BRACKETS
LINE_BREAK = [r'\\']

VALID_NUMBER_REGEX = r"[-+]?([0-9]+|[0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([eE]-?[0-9]+)?"
