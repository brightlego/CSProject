INFIX_BINARY_SCORE = {'=': 0, '<': 1, '>': 1, '<=': 1, '>=': 1, '!=': 1, '=>': 2, '->': 2, '+': 10, '-': 10, '*': 20,
                      '/': 20, '^': 30, '_': 1000, '.': 1100, ',': 0.5}

POSTFIX_UNARY_SCORE = {'!': 40}

PREFIX_UNARY_SCORE = {'-': 1100}

NON_ALPHA_IDENTIFIERS = ''
START_BRACKETS = '([{'
END_BRACKETS = ')]}'