from Symbol import Symbol

class SymbolTable:
    def __init__(self):
        self.count = {
            "static": 0,
            "field": 0,
            "arg": 0,
            "var": 0
        }
        self.class_name = None
        self.class_scope = {}
        self.subroutine_scope = {}

    def set_class_name(self, name):
        self.class_name = name

    def get_class(self):
        return self.class_name
    
    def start_subroutine(self):
        self.subroutine_scope = {}

    def increment_and_get_index(self, kind):
        current = self.count[kind]
        self.count[kind] = current + 1
        return self.count[kind]
    
    def define(self, name, typing, kind):
        index = self.increment_and_get_index(kind)
        if kind in ["static", "field"]:
            self.class_scope[name] = Symbol(typing, kind, index)
        elif kind in ["arg", "var"]:
            self.subroutine_scope[name] = Symbol(typing, kind, index)
        else:
            raise Exception("Incorrect identifier kind: {}".format(kind))
    
    def var_count(self, kind):
        return self.count[kind]

    def get_symbol(self, name):
        if name in self.class_scope.keys():
            return self.class_scope[name]
        elif name in self.subroutine_scope.keys():
            return self.subroutine_scope[name]
        else:
            return None
    
    def kind_of(self, name):
        return self.get_symbol(name).get_kind()

    def type_of(self, name):
        return self.get_symbol(name).get_type()

    def index_of(self, name):
        return self.get_symbol(name).get_index()