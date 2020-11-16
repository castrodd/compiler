class VMWriter:
    def __init__(self, output_file):
        self.output = output_file
    
    def write_push(self, segment, index):
        self.output.write("push {} {}\n".format(segment, index))

    def write_pop(self, segment, index):
        self.output.write("pop {} {}\n".format(segment, index))

    def write_artihmetic(self, command):
        self.output.write("{}\n".format(command))

    def write_label(self, label):
        self.output.write("label {}\n".format(label))

    def write_goto(self, label):
        self.output.write("goto {}\n".format(label))

    def write_if(self, label):
        self.output.write("if-goto {}\n".format(label))

    def write_call(self, name, nArgs):
        self.output.write("call {} {}\n".format(name, nArgs))

    def write_function(self, name, nLocals):
        self.output.write("function {} {}\n".format(name, nLocals))

    def write_return(self):
        self.output.write("return\n")

    def close(self):
        self.output.close()