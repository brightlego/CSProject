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
    def __init__(self, func, name=None):
        self.func = func
        self.name = name
        super().__init__()

    def apply(self, parameter):
        return self.func(parameter)

    def __repr__(self):
        if self.name is None:
            return f"<Builtin {self.func.__name__}>"
        else:
            return f"<Builtin {self.name}>"


class IdentifierName(Function):
    def __init__(self, name):
        self.name = name
        super().__init__()

    def __repr__(self):
        return f"<id {self.name}>"


class Tuple(Function):
    def __init__(self, item1=None, item2=None):
        self.item1 = item1
        self.item2 = item2
        super().__init__()

    def pre_add_item(self, item):
        if self.item2 is None:
            self.item2 = self.item1
            self.item1 = item
        else:
            self.item2 = Tuple(self.item1, self.item2)
            self.item1 = item

    def add_item(self, item):
        if isinstance(item, Tuple):
            if self.item1 is None:
                self.item1 = item.item1
                self.item2 = item.item2
            elif self.item2 is None:
                self.item2 = item
            elif isinstance(self.item2, Tuple):
                self.item2.add_item(item)
            else:
                self.item2 = Tuple(self.item2, item)

        if self.item1 is None:
            self.item1 = item
        elif self.item2 is None:
            self.item2 = item
        elif isinstance(self.item2, Tuple):
            self.item2.add_item(item)
        else:
            self.item2 = Tuple(self.item2, item)

    def get_item(self, index):
        length = self.get_length()
        if index >= length or index <= -1:
            return None
        elif length <= 2 and index == 1:
            return self.item2
        elif length <= 2 and index == 0:
            return self.item1
        elif index == length - 1:
            return self.item2
        else:
            return self.item1.get_item(index)

    def get_length(self):
        if self.item1 is None:
            if self.item2 is None:
                return 0
            else:
                return 1
        elif isinstance(self.item1, Tuple):
            return 1 + self.item1.get_length()
        else:
            return 2
