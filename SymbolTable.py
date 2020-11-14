from Symbol import Symbol

class SymbolTable:
    def __init__(self):
        self.count = {
            "STATIC": 0,
            "FIELD": 0,
            "ARG": 0,
            "VAR": 0
        }
        self.class_scope = {}
        self.subroutine_scope = {}
    
    def startSubroutine(self):
        self.subroutine_scope = {}

    def increment_and_get_index(self, kind):
        current = self.count[kind]
        self.count[kind] = current + 1
        return self.count[kind]
    
    def define(self, name, typing, kind):
        index = self.increment_and_get_index(kind)
        if kind in ["STATIC", "FIELD"]:
            self.class_scope[name] = Symbol(typing, kind, index)
        elif kind in ["ARG", "VAR"]:
            self.subroutine_scope[name] = Symbol(typing, kind, index)
        else:
            return Exception("Incorrect identifier kind: {}".format(kind))
    
    def var_count(self, kind):
        return self.count[kind]

    def get_symbol(self, name):
        if name in self.class_scope.keys():
            return self.class_scope[name]
        elif name in self.subroutine_scope.keys():
            return self.subroutine_scope[name]
        else:
            return Exception("Missing symbol of name {}".format(name))
    
    def kind_of(self, name):
        return self.get_symbol(name).get_kind()

    def type_of(self, name):
        return self.get_symbol(name).get_type()

    def index_of(self, name):
        return self.get_symbol(name).get_index()
