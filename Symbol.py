class Symbol:
    def __init__(self, typing, kind, number):
        self.typing = typing
        self.kind = kind
        self.number = number

    def get_type(self):
        return self.typing

    def get_kind(self):
        return self.kind

    def get_index(self):
        return self.number
