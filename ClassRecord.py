class ClassRecord:
    def __init__(self):
        self.classes = ["Math", "String", "Array", "Output", "Screen", "Keyboard", "Memory", "Sys"]
    
    def add_name(self, name):
        self.classes.append(name)
    
    def exists(self, name):
        return name in self.classes