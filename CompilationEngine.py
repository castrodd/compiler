class CompilationEngine:
    def __init__(self, input, output):
        self.tokenizer = input
        self.output = output
        while self.tokenizer.hasMoreTokens():
            self.compile_class()

    def verify_and_output_token(self, string):
        if self.tokenizer.token() != string:
            raise Exception("Expected {}; received {}".format(string, self.tokenizer.token()))
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
        
        self.output.write("\t<{tType}> {t} </{tType}>\n".format(tType=current_token_type, t=current_token))
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
        while self.tokenizer.token() in ["static", "field"]:
            self.compile_class_var_dec()
        while self.tokenizer.token() in ["constructor", "function", "method"]:
            self.compile_subroutine()
        self.verify_and_output_token("}")
        self.output_closing_tag("class")

    def compile_class_var_dec(self):
        self.output_opening_tag("classVarDec")
        if self.tokenizer.token() == "static" or self.tokenizer.token() == "field":
            self.output_token()
        else:
            raise Exception("Incorrect syntax for class variable declaration.")
        
        self.compile_type()
        self.output_token()
        while self.tokenizer.token() == ",":
            self.verify_and_output_token(",")
            self.output_token()

        self.verify_and_output_token(";")
        self.output_closing_tag("classVarDec")

    def compile_type(self):
        current_token = self.tokenizer.token()
        if current_token == "int" or current_token == "char" or current_token == "boolean":
            self.output_token()
        elif "identifier" in self.tokenizer.token_type():
            self.output_token()
        else:
            raise Exception("Incorrect syntax for type.")

    def is_type(self):
        current_token = self.tokenizer.token()
        if current_token == "int" or current_token == "char" or current_token == "boolean":
            return True
        elif "identifier" in self.tokenizer.token_type():
            return True
        else:
            return False

    def compile_subroutine(self):
        self.output_opening_tag("subroutineDec")
        
        current_token = self.tokenizer.token()
        if current_token == "constructor" or current_token == "function" or current_token == "method":
            self.output_token()
        else:
            raise Exception("Incorrect syntax for subroutine declaration.")

        if self.tokenizer.token() == "void":
            self.output_token()
        else:
            self.compile_type()

        self.output_token()
        self.verify_and_output_token("(")
        self.compile_parameter_list()
        self.verify_and_output_token(")")

        self.output_opening_tag("subroutineBody")
        self.verify_and_output_token("{")
        while self.tokenizer.token() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.verify_and_output_token("}")
        self.output_closing_tag("subroutineBody")
        self.output_closing_tag("subroutineDec")

    def compile_parameter_list(self):
        self.output_opening_tag("parameterList")
        while self.is_type():
            self.compile_type()
            self.output_token()
            while self.tokenizer.token() == ",":
                self.verify_and_output_token(",")
                self.compile_type()
                self.output_token()
        self.output_closing_tag("parameterList")

    def compile_var_dec(self):
        self.output_opening_tag("varDec")
        self.verify_and_output_token("var")
        self.compile_type()
        self.output_token()
        while self.tokenizer.token() == ",":
            self.verify_and_output_token(",")
            self.output_token()
        self.verify_and_output_token(";")
        self.output_closing_tag("varDec")

    def compile_statements(self):
        self.output_opening_tag("statements")
        while self.tokenizer.token() in ["let", "if", "while", "do", "return"]:
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
                raise Exception("Incorrect syntax for statement.")
        self.output_closing_tag("statements")

    def compile_do(self):
        self.output_opening_tag("doStatement")
        self.verify_and_output_token("do")
        
        self.tokenizer.advance()
        next_token = self.tokenizer.token()
        self.tokenizer.reverse()

        self.compile_subroutine_call(next_token)

        self.verify_and_output_token(";")
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
        self.output_closing_tag("whileStatement")

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
        self.output_opening_tag("expression")
        self.compile_term()
        while self.is_op():
            self.output_token()
            self.compile_term()
        self.output_closing_tag("expression")

    def compile_term(self):
        self.output_opening_tag("term")

        current_token = self.tokenizer.token()
        current_token_type = self.tokenizer.token_type()
        simple_terms = ["integerConstant", "stringConstant"]
        keyword_constants = ["true", "false", "null", "this"]
        
        if current_token_type in simple_terms or current_token in keyword_constants: 
            self.output_token()
        elif current_token == "(":
            self.verify_and_output_token("(")
            self.compile_expression()
            self.verify_and_output_token(")")
        elif current_token == "-" or current_token == "~":
            self.output_token()
            self.compile_term()
        elif "identifier" in current_token_type:
            self.tokenizer.advance()
            next_token = self.tokenizer.token()
            self.tokenizer.reverse()
            if next_token == "[":
                self.output_token()
                self.verify_and_output_token("[")
                self.compile_expression()
                self.verify_and_output_token("]")
            elif next_token == "(" or next_token == ".":
                self.compile_subroutine_call(next_token)
            else:
                self.output_token()
        else:
            raise Exception("Incorrect syntax for term.")
        
        self.output_closing_tag("term")
    
    def compile_subroutine_call(self, token):
        if token == "(":
            self.output_token()
            self.verify_and_output_token("(")
            self.compile_expression_list()
            self.verify_and_output_token(")")
        elif token == ".":
            self.output_token()
            self.verify_and_output_token(".")
            self.output_token()
            self.verify_and_output_token("(")
            self.compile_expression_list()
            self.verify_and_output_token(")")
        else:
            raise Exception("Incorrect syntax for subroutine call.")

    def is_op(self):
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        if self.tokenizer.token() in ops:
            return True
        return False

    def compile_expression_list(self):
        self.output_opening_tag("expressionList")
        if self.is_expression():
            self.compile_expression()
            while self.tokenizer.token() == ",":
                self.output_token()
                self.compile_expression()
        self.output_closing_tag("expressionList")
    
    def is_expression(self):
        expression_types = ["integerConstant", "stringConstant", "keyword"]
        token_type = self.tokenizer.token_type()
        symbols = ["(", "~", "-"]
        if token_type in expression_types or "identifier" in token_type or self.tokenizer.token() in symbols:
            return True
        return False