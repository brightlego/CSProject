import evaluator.builtins.types
import numpy as np


def add(x):
    def partial_add(y):
        if isinstance(y, evaluator.builtins.types.Number):
            return evaluator.builtins.types.Number(x.value + y.value)
        else:
            raise ValueError

    if isinstance(x, evaluator.builtins.types.Number):
        return evaluator.builtins.types.Builtin(partial_add)
    else:
        raise ValueError


def sub(x):
    def partial_sub(y):
        if isinstance(y, evaluator.builtins.types.Number):
            return evaluator.builtins.types.Number(x.value - y.value)
        else:
            raise ValueError

    if isinstance(x, evaluator.builtins.types.Number):
        return evaluator.builtins.types.Builtin(partial_sub)
    else:
        raise ValueError


def mul(x):
    def partial_mul(y):
        if isinstance(y, evaluator.builtins.types.Number):
            return evaluator.builtins.types.Number(x.value * y.value)
        else:
            raise ValueError

    if isinstance(x, evaluator.builtins.types.Number):
        return evaluator.builtins.types.Builtin(partial_mul)
    else:
        raise ValueError


def div(x):
    def partial_div(y):
        if isinstance(y, evaluator.builtins.types.Number):
            return evaluator.builtins.types.Number(x.value / y.value)
        else:
            raise ValueError

    if isinstance(x, evaluator.builtins.types.Number):
        return evaluator.builtins.types.Builtin(partial_div)
    else:
        raise ValueError


def neg(x):
    if isinstance(x, evaluator.builtins.types.Number):
        return evaluator.builtins.types.Number(-x.value)
    else:
        raise ValueError


def pow_(x):
    def partial_pow(y):
        if isinstance(y, evaluator.builtins.types.Number):
            return evaluator.builtins.types.Number(x.value ** y.value)
        else:
            raise ValueError

    if isinstance(x, evaluator.builtins.types.Number):
        return evaluator.builtins.types.Builtin(partial_pow)
    else:
        raise ValueError


def ignore(x):
    return x


OPERATORS = {
    '+': evaluator.builtins.types.Builtin(add),
    '-': evaluator.builtins.types.Builtin(sub),
    '*': evaluator.builtins.types.Builtin(mul),
    '/': evaluator.builtins.types.Builtin(div),
    '^': evaluator.builtins.types.Builtin(pow_),
    'negate': evaluator.builtins.types.Builtin(neg),
    'ignore': evaluator.builtins.types.Builtin(ignore)
}