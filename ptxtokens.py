class Token(object):
    pass

class Hexadecimal(Token):
    def __init__(self, t):
        self.args = []
        self.unsigned = t[-1] == "U"
        if self.unsigned:
            self.value = int(t[2:-1], base=16)
        else:
            self.value = int(t[2:], base=16)

    def __str__(self):
        return f"Hex(0x{self.value:x},unsigned={self.unsigned})"

    __repr__ = __str__

class Octal(Token):
    def __init__(self, t):
        self.args = []
        self.unsigned = t[-1] == "U"
        if self.unsigned:
            self.value = int(t[1:-1], base=8)
        else:
            self.value = int(t[1:], base=8)

    def __str__(self):
        return f"Octal(0{self.value:o},unsigned={self.unsigned})"

    __repr__ = __str__

class Binary(Token):
    def __init__(self, t):
        self.args = []
        self.unsigned = t[-1] == "U"
        if self.unsigned:
            self.value = int(t[2:-1], base=2)
        else:
            self.value = int(t[2:], base=2)

    def __str__(self):
        return f"Octal(0b{self.value:b},unsigned={self.unsigned})"

    __repr__ = __str__

class Decimal(Token):
    def __init__(self, t):
        self.args = []
        self.unsigned = t[-1] == "U"
        if self.unsigned:
            self.value = int(t[:-1], base=10)
        else:
            self.value = int(t, base=10)

    def __str__(self):
        return f"Decimal({self.value},unsigned={self.unsigned})"

    __repr__ = __str__

