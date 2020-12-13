from Symbol import Symbol

class SymbolTable:
    def __init__(self):
        self.count = {
            "static": -1,
            "field": -1,
            "argument": -1,
            "var": -1
        }
        self.class_name = None
        self.class_scope = {}
        self.subroutine_scope = {}

    def set_class_name(self, name):
        self.class_name = name

    def get_class(self):
        return self.class_name
    
    def get_class_scope_keys(self):
        return self.class_scope.keys()
    
    def get_subroutine_scope_keys(self):
        return self.subroutine_scope.keys()
    
    def start_subroutine(self):
        self.subroutine_scope = {}
        self.reset_count("argument")
        self.reset_count("var")

    def reset_count(self, kind):
        self.count[kind] = -1

    def increment_and_get_index(self, kind):
        current = self.count[kind]
        self.count[kind] = current + 1
        return self.count[kind]
    
    def define(self, name, typing, kind):
        if self.exists(name, kind):
            return 0

        index = self.increment_and_get_index(kind)
        if kind in ["static", "field"]:
            self.class_scope[name] = Symbol(typing, kind, index)
        elif kind in ["argument", "var"]:
            self.subroutine_scope[name] = Symbol(typing, kind, index)
        else:
            raise Exception("Incorrect identifier kind: {}".format(kind))

    def exists(self, name, kind):
        if kind in ["static", "field"] and name in self.get_class_scope_keys():
            return True
        elif kind in ["argument", "var"] and name in self.get_subroutine_scope_keys():
            return True
        else:
            return False
    
    def var_count(self, kind):
        return self.count[kind] + 1

    def get_symbol(self, name):
        if name in self.class_scope.keys():
            return self.class_scope[name]
        elif name in self.subroutine_scope.keys():
            return self.subroutine_scope[name]
        else:
            return None

    def get_class_symbol(self, name):
        if name in self.class_scope.keys():
            return self.class_scope[name]

    def get_subroutine_symbol(self, name):
        if name in self.subroutine_scope.keys():
            return self.subroutine_scope[name]
    
    def kind_of(self, name):
        return self.get_symbol(name).get_kind()

    def type_of(self, name):
        return self.get_symbol(name).get_type()

    def index_of(self, name):
        return self.get_symbol(name).get_index()
