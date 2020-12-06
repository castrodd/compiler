class ClassRecord:
    os = ["Math", "String", "Array", "Output", "Screen", "Keyboard", "Memory", "Sys"]

    def __init__(self):
        self.classes = []

    def add_name(self, name):
        self.classes.append(name)
    
    def exists(self, name):
        return name in self.classes or name in ClassRecord.os
    
    @staticmethod
    def is_os(name):
        return name in ClassRecord.os