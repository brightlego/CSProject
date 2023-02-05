import types
import numpy as np


def add(x):
    def partial_add(y):
        if isinstance(y, types.Number):
            return types.Number(x.value + y.value)
        else:
            raise ValueError

    if isinstance(x, types.Number):
        return types.Builtin(partial_add)
    else:
        raise ValueError


def sub(x):
    def partial_sub(y):
        if isinstance(y, types.Number):
            return types.Number(x.value - y.value)
        else:
            raise ValueError

    if isinstance(x, types.Number):
        return types.Builtin(partial_sub)
    else:
        raise ValueError


def mul(x):
    def partial_mul(y):
        if isinstance(y, types.Number):
            return types.Number(x.value * y.value)
        else:
            raise ValueError

    if isinstance(x, types.Number):
        return types.Builtin(partial_mul)
    else:
        raise ValueError


def div(x):
    def partial_div(y):
        if isinstance(y, types.Number):
            return types.Number(x.value / y.value)
        else:
            raise ValueError

    if isinstance(x, types.Number):
        return types.Builtin(partial_div)
    else:
        raise ValueError


def neg(x):
    if isinstance(x, types.Number):
        return types.Number(-x.value)
    else:
        raise ValueError


def pow_(x):
    def partial_pow(y):
        if isinstance(y, types.Number):
            return types.Number(x.value ** y.value)
        else:
            raise ValueError

    if isinstance(x, types.Number):
        return types.Builtin(partial_pow)
    else:
        raise ValueError


def ignore(x):
    return x


OPERATORS = {
    '+': types.Builtin(add),
    '-': types.Builtin(sub),
    '*': types.Builtin(mul),
    '/': types.Builtin(div),
    '^': types.Builtin(pow_),
    'negate': types.Builtin(neg),
    'ignore': types.Builtin(ignore)
}