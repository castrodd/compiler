from VMWriter import VMWriter

class CompilationEngine:
    def __init__(self, input, output):
        self.tokenizer = input
        self.writer = VMWriter(output)
        self.class_name = None
        self.label_count = 1
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
        total_parameters = 0
        if current_token == "constructor" or current_token == "function":
            self.advance_token()
        elif current_token == "method":
            total_parameters += 1
            self.writer.write_push("argument", 0)
            self.writer.write_pop("pointer", 0)
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

        self.writer.write_function("{}.{}".format(self.class_name, subroutine_name), total_parameters)

        # Subroutine body
        #    { symbol
        self.verify_token("{")
        # Subroutine variable declarations
        while self.tokenizer.token() == "var":
            self.compile_var_dec()
        # Subroutine statements
        self.compile_statements(is_void)
        # } symbol
        self.verify_token("}")

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

    def compile_statements(self, *args):
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
                if len(args) > 0:
                    self.compile_return(args[0])
                else:
                    self.compile_return(False)
            else:
                raise Exception("Incorrect syntax for statement.")

    def compile_do(self):
        self.verify_token("do")
        
        self.tokenizer.advance()
        next_token = self.tokenizer.token()
        self.tokenizer.reverse()

        self.compile_subroutine_call(next_token)
        self.verify_token(";")
        self.writer.write_pop("temp", 0)

    def compile_let(self):
        self.verify_token("let")

        current_var = self.tokenizer.token_type()
        current_var_kind = current_var.split(".")[1]
        current_var_index = current_var.split(".")[-1]
        if "field" in current_var_kind:
            current_var_kind = "this"
        elif "var" in current_var_kind:
            current_var_kind = "local"
        
        self.advance_token()
        
        if self.tokenizer.token() == "[":
            self.verify_token("[")
            self.compile_expression()
            self.verify_token("]")
        
        self.verify_token("=")
        self.compile_expression()
        self.verify_token(";")

        self.writer.write_pop(current_var_kind, current_var_index)

    def compile_while(self):
        label_one,label_two = self.create_labels()
        
        self.writer.write_label(label_one)
        self.verify_token("while")
        self.verify_token("(")
        self.compile_expression()
        self.verify_token(")")

        self.writer.write_artihmetic("not")
        self.writer.write_if(label_two)

        self.verify_token("{")
        self.compile_statements()
        self.verify_token("}")

        self.writer.write_goto(label_one)
        self.writer.write_label(label_two)

    def compile_return(self, is_void):
        self.verify_token("return")
        if self.tokenizer.token() == ";":
            self.verify_token(";")
            if is_void:
                self.writer.write_push("constant", 0)
            self.writer.write_return()
        else:
            self.compile_expression()
            self.advance_token()

    def compile_if(self):
        label_one,label_two = self.create_labels()

        self.verify_token("if")
        self.verify_token("(")
        self.compile_expression()
        self.verify_token(")")

        self.writer.write_artihmetic("not")
        self.writer.write_if(label_one)

        self.verify_token("{")
        self.compile_statements()
        self.verify_token("}")

        self.writer.write_goto(label_two)
        self.writer.write_label(label_one)

        if self.tokenizer.token() == "else":
            self.verify_token("else")
            self.verify_token("{")
            self.compile_statements()
            self.verify_token("}")
        
        self.writer.write_label(label_two)

    def create_labels(self):
        label_one = "L{}".format(self.label_count)
        self.label_count += 1
        label_two = "L{}".format(self.label_count)
        self.label_count += 1
        return (label_one, label_two)

    def compile_expression(self):
        self.compile_term()
        while self.is_op():
            current_op = self.tokenizer.token()
            self.advance_token()
            self.compile_term()
            self.write_op(current_op)

    def compile_term(self):
        current_token = self.tokenizer.token()
        current_token_type = self.tokenizer.token_type()
        simple_terms = ["integerConstant", "stringConstant"]
        keyword_constants = ["true", "false", "null", "this"]
        
        if current_token_type == "integerConstant":
            self.writer.write_push("constant", current_token)
            self.advance_token()
        elif current_token_type in simple_terms or current_token in keyword_constants: 
            self.advance_token()
        elif current_token == "(":
            self.verify_token("(")
            self.compile_expression()
            self.verify_token(")")
        elif current_token == "-" or current_token == "~":
            self.advance_token()
            self.compile_term()
        elif "identifier" in current_token_type:
            self.tokenizer.advance()
            next_token = self.tokenizer.token()
            self.tokenizer.reverse()
            if next_token == "[":
                self.advance_token()
                self.verify_token("[")
                self.compile_expression()
                self.verify_token("]")
            elif next_token == "(" or next_token == ".":
                self.compile_subroutine_call(next_token)
            else:
                self.advance_token()
        else:
            raise Exception("Incorrect syntax for term.")
    
    def write_op(self, op_symbol):
        if op_symbol == "+":
            self.writer.write_artihmetic("add")
        elif op_symbol == "-":
            self.writer.write_artihmetic("sub")
        elif op_symbol == "-":
            self.writer.write_artihmetic("neg")
        elif op_symbol == "=":
            self.writer.write_artihmetic("eq")
        elif op_symbol == ">":
            self.writer.write_artihmetic("gt")
        elif op_symbol == "<":
            self.writer.write_artihmetic("lt")
        elif op_symbol == "&":
            self.writer.write_artihmetic("and")
        elif op_symbol == "|":
            self.writer.write_artihmetic("or")
        elif op_symbol == "!":
            self.writer.write_artihmetic("not")
        elif op_symbol == "*":
            self.writer.write_call("Math.multiply", 2)

    
    def compile_subroutine_call(self, token):
        if token == "(":
            self.advance_token()
            self.verify_token("(")
            self.compile_expression_list()
            self.verify_token(")")
        elif token == ".":
            # Class
            class_token = self.tokenizer.token()
            self.advance_token()
            # . symbol
            self.verify_token(".")
            # Subroutine name
            subroutine_name = self.tokenizer.token()
            self.advance_token()
            # ( symbol
            self.verify_token("(")
            # Expression list
            total_arguments = self.compile_expression_list()
            # ) symbol
            self.verify_token(")")
            self.writer.write_call("{}.{}".format(class_token, subroutine_name), total_arguments)
        else:
            raise Exception("Incorrect syntax for subroutine call.")

    def is_op(self):
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        if self.tokenizer.token() in ops:
            return True
        return False

    def compile_expression_list(self):
        total_arguments = 0
        if self.is_expression():
            total_arguments += 1
            self.compile_expression()
            while self.tokenizer.token() == ",":
                self.advance_token()
                total_arguments += 1
                self.compile_expression()
        return total_arguments
    
    def is_expression(self):
        expression_types = ["integerConstant", "stringConstant", "keyword"]
        token_type = self.tokenizer.token_type()
        symbols = ["(", "~", "-"]
        if token_type in expression_types or "identifier" in token_type or self.tokenizer.token() in symbols:
            return True
        return False