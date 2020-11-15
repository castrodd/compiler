from VMWriter import VMWriter

class CompilationEngine:
    def __init__(self, input, symbol_table, output):
        self.tokenizer = input
        self.writer = VMWriter(output)
        self.symbol_table = symbol_table
        self.class_name = None
        while self.tokenizer.hasMoreTokens():
            self.compile_class()
        self.writer.close()

    def verify_token(self, string):
        if self.tokenizer.token() != string:
            raise Exception("Expected {}; received {}".format(string, self.tokenizer.token()))
        else:
            self.tokenizer.advance()

    def advance_token(self):
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
        #self.output.write("\t<{tType}> {t} </{tType}>\n".format(tType=current_token_type, t=current_token))
        self.tokenizer.advance()

    def compile_class(self):
        # Class keyword
        self.verify_token("class")
        # Class name
        self.class_name = self.tokenizer.token()
        self.advance_token()
        # { symbol
        self.verify_token("{")
        # Class variable declarations
        while self.tokenizer.token() in ["static", "field"]:
            self.compile_class_var_dec()
        # Class subroutines
        while self.tokenizer.token() in ["constructor", "function", "method"]:
            self.compile_subroutine()
        # } symbol
        self.verify_token("}")

    def compile_class_var_dec(self):
        # Class variable kind
        if self.tokenizer.token() == "static" or self.tokenizer.token() == "field":
            self.advance_token()
        else:
            raise Exception("Incorrect syntax for class variable declaration.")
        # Class variable type
        self.validate_type()
        # Class variable name
        self.advance_token()
        # Handle list of variables
        while self.tokenizer.token() == ",":
            self.verify_token(",")
            self.advance_token()
        # ; symbol
        self.verify_token(";")

    def validate_type(self):
        current_token = self.tokenizer.token()
        if current_token == "int" or current_token == "char" or current_token == "boolean":
            self.advance_token()
        elif "identifier" in self.tokenizer.token_type():
            self.advance_token()
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
        # Subroutine type
        current_token = self.tokenizer.token()
        if current_token == "constructor" or current_token == "function":
            self.advance_token()
        elif current_token == "method":
            total_parameters = 1
            self.advance_token()
        else:
            raise Exception("Incorrect syntax for subroutine declaration.")
        
        # Return type
        if self.tokenizer.token() == "void":
            is_void = True
            self.advance_token()
        else:
            is_void = False
            self.validate_type()

        # Subroutine name
        subroutine_name = self.tokenizer.token()
        self.advance_token()
        # ( symbol
        self.verify_token("(")
        #Parameter list
        total_parameters += self.compile_parameter_list()
        # ) symbol
        self.verify_token(")")

        self.writer.write_function(subroutine_name, total_parameters)

        # Subroutine body
        #    { symbol
        self.verify_token("{")
        # Subroutine variable declarations
        while self.tokenizer.token() == "var":
            self.compile_var_dec()
        # Subroutine statements
        self.compile_statements()
        # } symbol
        self.verify_token("}")

        if is_void:
            self.writer.write_push("constant", 0)
        self.writer.write_return()


    def compile_parameter_list(self):
        total_parameters = 0
        while self.is_type():
            # Variable type
            self.validate_type()
            # Variable name
            self.advance_token()
            total_parameters += 1
            # Further parameters
            while self.tokenizer.token() == ",":
                self.verify_token(",")
                self.validate_type()
                self.advance_token()
                total_parameters += 1
        return total_parameters

    def compile_var_dec(self):
        # Variable declarations
        self.verify_token("var")
        self.validate_type()
        self.advance_token()
        while self.tokenizer.token() == ",":
            self.verify_token(",")
            self.advance_token()
        self.verify_token(";")

    def compile_statements(self):
        # Statement keyword
        while self.tokenizer.token() in ["let", "if", "while", "do", "return"]:
            token = self.tokenizer.token()
            if token == "let":
                self.compile_let()
            elif token == "if":
                self.compile_if()
            elif token == "while":
                self.compile_while()
            elif token == "do":
                self.compile_do()
            elif token == "return":
                self.compile_return()
            else:
                raise Exception("Incorrect syntax for statement.")

    def compile_do(self):
        # Do keyword
        self.verify_token("do")
        
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