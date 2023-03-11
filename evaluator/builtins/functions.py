import builtins

import evaluator.builtins.types
import evaluator.execution_tree

import numpy as np

OPERATORS = {'i': evaluator.builtins.types.Number(1j),
             'pi': evaluator.builtins.types.Number(np.pi),
             'e': evaluator.builtins.types.Number(np.e)}

executor = None

def validate_type(input_type):
    def _validate(function):
        def validated_function(var_in):
            if isinstance(var_in, input_type):
                return function(var_in)
            else:
                raise ValueError
        return validated_function
    return _validate


def builtin_func(name, operator=None):
    def _builtin(function):
        out = evaluator.builtins.types.Builtin(function, name)
        if operator is None:
            OPERATORS[name] = out
        else:
            OPERATORS[operator] = out
        return out

    return _builtin


@builtin_func("add", '+')
@validate_type(evaluator.builtins.types.Number)
def add(x):
    @validate_type(evaluator.builtins.types.Number)
    def partial_add(y):
        return evaluator.builtins.types.Number(x.value + y.value)

    return evaluator.builtins.types.Builtin(partial_add)


@builtin_func("sub", '-')
@validate_type(evaluator.builtins.types.Number)
def sub(x):
    @validate_type(evaluator.builtins.types.Number)
    def partial_sub(y):
        return evaluator.builtins.types.Number(x.value - y.value)

    return evaluator.builtins.types.Builtin(partial_sub)


@builtin_func("mul", '*')
@validate_type(evaluator.builtins.types.Number)
def mul(x):
    @validate_type(evaluator.builtins.types.Number)
    def partial_mul(y):
        return evaluator.builtins.types.Number(x.value * y.value)

    return evaluator.builtins.types.Builtin(partial_mul)


@builtin_func("div", '/')
@validate_type(evaluator.builtins.types.Number)
def div(x):
    @validate_type(evaluator.builtins.types.Number)
    def partial_div(y):
        return evaluator.builtins.types.Number(x.value / y.value)

    return evaluator.builtins.types.Builtin(partial_div)


@builtin_func("neg", 'negate')
@validate_type(evaluator.builtins.types.Number)
def neg(x):
    return evaluator.builtins.types.Number(-x.value)


@builtin_func("pow", '^')
@validate_type(evaluator.builtins.types.Number)
def pow_(x):
    @validate_type(evaluator.builtins.types.Number)
    def partial_pow(y):
        return evaluator.builtins.types.Number(x.value ** y.value)
    return evaluator.builtins.types.Builtin(partial_pow)


@builtin_func("ignore")
def ignore(x):
    return x


@builtin_func("cos")
@validate_type(evaluator.builtins.types.Number)
def cos(x):
    return evaluator.builtins.types.Number(np.cos(x.value))


@builtin_func("sin")
@validate_type(evaluator.builtins.types.Number)
def sin(x):
    return evaluator.builtins.types.Number(np.sin(x.value))


@builtin_func("tan")
@validate_type(evaluator.builtins.types.Number)
def tan(x):
    return evaluator.builtins.types.Number(np.tan(x.value))


@builtin_func("acos")
@validate_type(evaluator.builtins.types.Number)
def acos(x):
    return evaluator.builtins.types.Number(np.arccos(x.value))


@builtin_func("asin")
@validate_type(evaluator.builtins.types.Number)
def asin(x):
    return evaluator.builtins.types.Number(np.arcsin(x.value))


@builtin_func("atan")
@validate_type(evaluator.builtins.types.Number)
def atan(x):
    return evaluator.builtins.types.Number(np.arctan(x.value))


@builtin_func("cosh")
@validate_type(evaluator.builtins.types.Number)
def cosh(x):
    return evaluator.builtins.types.Number(np.cosh(x.value))


@builtin_func("sinh")
@validate_type(evaluator.builtins.types.Number)
def sinh(x):
    return evaluator.builtins.types.Number(np.sinh(x.value))


@builtin_func("tanh")
@validate_type(evaluator.builtins.types.Number)
def tanh(x):
    return evaluator.builtins.types.Number(np.tanh(x.value))


@builtin_func("acosh")
@validate_type(evaluator.builtins.types.Number)
def acosh(x):
    return evaluator.builtins.types.Number(np.arccosh(x.value))


@builtin_func("asinh")
@validate_type(evaluator.builtins.types.Number)
def asinh(x):
    return evaluator.builtins.types.Number(np.arcsinh(x.value))


@builtin_func("atanh")
@validate_type(evaluator.builtins.types.Number)
def atanh(x):
    return evaluator.builtins.types.Number(np.arctan(x.value))


@builtin_func("ln")
@validate_type(evaluator.builtins.types.Number)
def ln(x):
    return evaluator.builtins.types.Number(np.log(x.value))


@builtin_func("log10", "log")
@validate_type(evaluator.builtins.types.Number)
def log10(x):
    return evaluator.builtins.types.Number(np.log10(x.value))


@builtin_func("log", "_log")
@validate_type(evaluator.builtins.types.Number)
def loga(a):
    @validate_type(evaluator.builtins.types.Number)
    def log_ab(x):
        return evaluator.builtins.types.Number(np.log(x.value)/np.log(a.value))

    return evaluator.builtins.types.Builtin(log_ab)


@builtin_func("underscore", "_")
def underscore(a):
    def _underscore(b):
        if a.name == 'log10' and isinstance(b, evaluator.builtins.types.Number):
            return loga.apply(b)
        else:
            raise ValueError

    return evaluator.builtins.types.Builtin(_underscore)


@builtin_func("tuple", ',')
def tuple_(x):
    def partial_tuple(y):
        return evaluator.builtins.types.Tuple(x, y)

    return evaluator.builtins.types.Builtin(partial_tuple)


@builtin_func("sqrt")
@validate_type(evaluator.builtins.types.Number)
def sqrt(x):
    return evaluator.builtins.types.Number(np.sqrt(x.value))


@builtin_func("integrate")
@validate_type(evaluator.builtins.types.Tuple)
def integrate(params):
    if params.get_length()  != 4:
        raise ValueError
    expression = params.get_item(0)
    identifier = params.get_item(1)
    low = params.get_item(2)
    high = params.get_item(3)

    if not isinstance(expression,
                      evaluator.execution_tree.ExecutionTree._ExecutionTree__Node):
        raise ValueError
    if not isinstance(identifier, evaluator.builtins.types.IdentifierName):
        raise ValueError
    if not isinstance(low, evaluator.builtins.types.Number):
        raise ValueError
    if not isinstance(high, evaluator.builtins.types.Number):
        raise ValueError

    total = 0

    dx = (high.value - low.value)/300

    for x in np.linspace(low.value, high.value, 300):
        result = executor.evaluate_function(expression, x, identifier.name.item)
        total += result

    total *= 2
    total -= executor.evaluate_function(expression, low.value,
                                        identifier.name.item)
    total -= executor.evaluate_function(expression, high.value,
                                        identifier.name.item)
    integral = total * dx/2
    return evaluator.builtins.types.Number(integral)


@builtin_func("re")
@validate_type(evaluator.builtins.types.Number)
def real(x):
    return evaluator.builtins.types.Number(np.real(x.value))


@builtin_func("im")
@validate_type(evaluator.builtins.types.Number)
def imag(x):
    return evaluator.builtins.types.Number(np.imag(x.value))


@builtin_func("conj")
@validate_type(evaluator.builtins.types.Number)
def conj(x):
    return evaluator.builtins.types.Number(np.conj(x.value))


@builtin_func("differentiate")
@validate_type(evaluator.builtins.types.Tuple)
def differentiate(params):
    if params.get_length() != 3:
        raise ValueError

    expression = params.get_item(0)
    identifier = params.get_item(1)
    value = params.get_item(2)
    if not isinstance(expression,
                      evaluator.execution_tree.ExecutionTree._ExecutionTree__Node):
        raise ValueError
    if not isinstance(identifier, evaluator.builtins.types.IdentifierName):
        raise ValueError
    if not isinstance(value, evaluator.builtins.types.Number):
        raise ValueError

    dx = 0.0000001
    result = (executor.evaluate_function(expression,
                                         value.value,
                                         identifier.name.item) -
              executor.evaluate_function(expression,
                                         value.value - dx,
                                         identifier.name.item)) / dx
    return evaluator.builtins.types.Number(result)