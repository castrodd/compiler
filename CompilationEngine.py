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
    
    def output_opening_tag(self, tag_name):
        self.output.write("<{tag}>\n".format(tag=tag_name))

    def output_closing_tag(self, tag_name):
        self.output.write("</{tag}>\n".format(tag=tag_name))

    def compile_class(self):
        self.output_opening_tag("class")
        self.verify_and_output_token("class")
        self.output_token()
        self.verify_and_output_token("{")
        self.compile_class_var_dec()
        self.compile_subroutine()
        self.verify_and_output_token("}")
        self.output_closing_tag("class")

    def compile_class_var_dec(self):
        self.output_opening_tag("classVarDec")
        
        self.output_closing_tag("classVarDec")

    def compile_subroutine(self):
        pass

    def compile_parameter_list(self):
        pass

    def compile_var_dec(self):
        pass

    def compile_statements(self):
        self.output_opening_tag("statements")
        while self.tokenizer.hasMoreTokens():
            current_token = self.tokenizer.token()
            if current_token == "let":
                self.compile_let()
            elif current_token == "if":
                self.compile_if()
            elif current_token == "while":
                self.compile_while()
            elif current_token == "do":
                self.compile_do()
            elif current_token == "return":
                self.compile_return()
            else:
                return Exception("Incorrect syntax for statement.")
        self.output_closing_tag("statements")

    def compile_do(self):
        self.output_opening_tag("doStatement")
        self.verify_and_output_token("do")
        self.output_token()
        if self.tokenizer.token() == "(":
            self.verify_and_output_token("(")
            self.compile_expression_list()
            self.verify_and_output_token(")")
        elif self.tokenizer.token() == ".":
            self.verify_and_output_token(".")
            self.output_token()
            self.verify_and_output_token("(")
            self.compile_expression_list()
            self.verify_and_output_token(")")
        else:
            return Exception("Incorrect syntax for Do Statement.")
        self.output_closing_tag("doStatement")

    def compile_let(self):
        self.output_opening_tag("letStatement")
        self.verify_and_output_token("let")
        self.output_token()
        if self.tokenizer.token() == "[":
            self.verify_and_output_token("[")
            self.compile_expression()
            self.verify_and_output_token("]")
        
        self.verify_and_output_token("=")
        self.compile_expression()
        self.verify_and_output_token(";")
        self.output_closing_tag("letStatement")

    def compile_while(self):
        self.output_opening_tag("whileStatement")
        self.verify_and_output_token("while")
        self.verify_and_output_token("(")
        self.compile_expression()
        self.verify_and_output_token(")")
        self.verify_and_output_token("{")
        self.compile_statements()
        self.verify_and_output_token("}")
        self.output_closing_tag("whileStatment")

    def compile_return(self):
        self.output_opening_tag("returnStatement")
        self.verify_and_output_token("return")
        if self.tokenizer.token() == ";":
            self.verify_and_output_token(";")
        else:
            self.compile_expression()
            self.output_token()
        self.output_closing_tag("returnStatement")

    def compile_if(self):
        self.output_opening_tag("ifStatement")
        self.verify_and_output_token("if")
        self.verify_and_output_token("(")
        self.compile_expression()
        self.verify_and_output_token(")")
        self.verify_and_output_token("{")
        self.compile_statements()
        self.verify_and_output_token("}")

        if self.tokenizer.token() == "else":
            self.verify_and_output_token("else")
            self.verify_and_output_token("{")
            self.compile_statements()
            self.verify_and_output_token("}")

        self.output_closing_tag("ifStatement")

    def compile_expression(self):
        pass

    def compile_term(self):
        pass

    def compile_expression_list(self):
        pass