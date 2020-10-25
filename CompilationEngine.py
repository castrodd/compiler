class CompilationEngine:
    def __init__(self, input, output):
        self.tokenizer = input
        self.output = output
        self.compile_class()

    def verify_and_output_token(self, string):
        if self.tokenizer.token() != string:
            return Exception("Expected {}; received {}".format(string, self.tokenizer.token()))
        else:
            self.output_token()

    def output_token(self):
        current_token = self.tokenizer.token()
        current_token_type = self.tokenizer.token_type()
        if current_token_type == "stringConstant":
            current_token = current_token[1:-1] # Strip quotation marks
        if current_token == "<":
            current_token = "&lt;"
        if current_token == ">":
            current_token = "&gt;"
        if current_token == "&":
            current_token = "&amp;"
        
        self.output.write("\t<{tType}>\n\t{t}\n</{tType}>\n".format(tType=current_token_type, t=current_token))
        self.tokenizer.advance()

    def compile_class(self):
        self.verify_and_output_token("class")
        self.output()
        self.verify_and_output_token("{")
        self.compile_class_var_dec()
        self.compile_subroutine()
        self.verify_and_output_token("}")


    def compile_class_var_dec(self):
        pass

    def compile_subroutine(self):
        pass

    def compile_parameter_list(self):
        pass

    def compile_var_dec(self):
        pass

    def compile_statements(self):
        pass

    def compile_do(self):
        pass

    def compile_let(self):
        pass
    def compile_while(self):
        pass

    def compile_return(self):
        pass

    def compile_if(self):
        pass

    def compile_expression(self):
        pass
    def compile_term(self):
        pass

    def compile_expression_list(self):
        pass