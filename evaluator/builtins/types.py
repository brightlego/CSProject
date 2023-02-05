class Function:
    def __init__(self):
        pass

    def apply(self, parameter):
        return Function()


class Number(Function):
    def __init__(self, value):
        self.value = value
        super().__init__()

    def apply(self, parameter):
        if isinstance(parameter, Number):
            return Number(self.value * parameter.value)

    def __repr__(self):
        return f"{self.value}"


class Builtin(Function):
    def __init__(self, func):
        self.func = func
        super().__init__()

    def apply(self, parameter):
        return self.func(parameter)

    def __repr__(self):
        return f"<Builtin {self.func.__name__}>"