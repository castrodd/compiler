from VMWriter import VMWriter
from ClassRecord import ClassRecord

class CompilationEngine:
    def __init__(self, input, output, class_record):
        # Initialize
        self.tokenizer = input
        self.writer = VMWriter(output)
        self.class_record = class_record
        self.class_name = None
        self.label_count = 1
        self.negative_term = False
        self.is_constructor = False
        self.is_method = False

        # Traverse tokenizer
        while self.tokenizer.hasMoreTokens():
            self.compile_class()

        # Close output file
        self.writer.close()
    
    def token(self):
        return self.tokenizer.token()

    def type(self):
        return self.tokenizer.token_type()

    def verify_token(self, string):
        if self.token() != string:
            raise Exception("Expected {}; received {}".format(string, self.token()))
        else:
            self.tokenizer.advance()

    def advance_token(self):
        current_token = self.token()
        current_token_type = self.type()
        if current_token_type == "stringConstant":
            current_token = current_token[1:-1] # Strip quotation marks
        if current_token == "<":
            current_token = "&lt;"
        if current_token == ">":
            current_token = "&gt;"
        if current_token == "&":
            current_token = "&amp;"
        self.tokenizer.advance()

    def reverse_token(self):
        self.tokenizer.reverse()

    def compile_class(self):
        # Class keyword
        self.verify_token("class")
        # Class name
        self.class_name = self.token()
        self.advance_token()
        # { symbol
        self.verify_token("{")
        # Class variable declarations
        while self.token() in ["static", "field"]:
            self.compile_class_var_dec()
        # Class subroutines
        while self.token() in ["constructor", "function", "method"]:
            self.compile_subroutine()
        # } symbol
        self.verify_token("}")

    def compile_class_var_dec(self):
        # Class variable kind
        if self.token() == "static" or self.token() == "field":
            self.advance_token()
        else:
            raise Exception("Incorrect syntax for class variable declaration.")
        # Class variable type
        self.validate_type()
        # Class variable name
        self.advance_token()
        # Handle list of variables
        while self.token() == ",":
            self.verify_token(",")
            self.advance_token()
        # ; symbol
        self.verify_token(";")

    def validate_type(self):
        current_token = self.token()
        if current_token == "int" or current_token == "char" or current_token == "boolean":
            self.advance_token()
        elif "identifier" in self.type():
            self.advance_token()
        else:
            raise Exception("Incorrect syntax for type.")

    def is_type(self):
        current_token = self.token()
        if current_token == "int" or current_token == "char" or current_token == "boolean":
            return True
        elif "identifier" in self.type():
            return True
        else:
            return False

    def compile_subroutine(self):
        # Subroutine type
        current_token = self.token()
        if current_token == "constructor":
            total_fields = self.type().split(".")[1]
            self.is_constructor = True
            self.advance_token()
        elif current_token == "function":
            self.advance_token()
        elif current_token == "method":
            self.is_method = True
            self.advance_token()
        else:
            raise Exception("Incorrect syntax for subroutine declaration.")
        
        # Return type
        if self.token() == "void":
            is_void = True
            self.advance_token()
        else:
            is_void = False
            self.validate_type()

        # Subroutine name
        subroutine_name = self.token()
        self.advance_token()
        # ( symbol
        self.verify_token("(")
        #Parameter list
        self.compile_parameter_list()
        # ) symbol
        self.verify_token(")")

        # Subroutine body
        #    { symbol
        self.verify_token("{")
        # Subroutine variable declarations
        total_vars = 0
        while self.token() == "var":
            total_vars += self.compile_var_dec()

        self.writer.write_function("{}.{}".format(self.class_name, subroutine_name), total_vars)
        if self.is_constructor:
            self.allocate_memory(total_fields)
        elif self.is_method:
            self.writer.write_push("argument", 0)
            self.writer.write_pop("pointer", 0)

        # Subroutine statements
        self.compile_statements(is_void)
        # } symbol
        self.verify_token("}")
        self.is_method = False
    
    def allocate_memory(self, total_fields):
        self.writer.write_push("constant", total_fields)
        self.writer.write_call("Memory.alloc", 1)
        self.writer.write_pop("pointer", 0)

    def compile_parameter_list(self):
        while self.is_type():
            # Variable type
            self.validate_type()
            # Variable name
            self.advance_token()
            # Further parameters
            while self.token() == ",":
                self.verify_token(",")
                self.validate_type()
                self.advance_token()

    def compile_var_dec(self):
        total_vars = 0

        # Variable declarations
        self.verify_token("var")
        self.validate_type()
        self.advance_token()
        total_vars += 1

        while self.token() == ",":
            self.verify_token(",")
            self.advance_token()
            total_vars += 1

        self.verify_token(";")
        return total_vars

    def compile_statements(self, *args):
        # Statement keyword
        while self.token() in ["let", "if", "while", "do", "return"]:
            token = self.token()
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
        # Verify in a do statement
        self.verify_token("do")
        
        # Peek at next token
        self.tokenizer.advance()
        next_token = self.token()
        self.tokenizer.reverse()

        # Translate segments
        current_token_type = self.type().split(".")
        current_segment = current_token_type[1]
        if current_segment == "var":
            current_segment = "local"
        if current_segment == "field":
            current_segment = "this"
        if current_segment == "subroutine":
            current_segment = "pointer"
        
        # Push onto the stack
        current_index = current_token_type[4]
        if not self.class_record.exists(self.token()): 
            self.writer.write_push(current_segment, current_index)

        # Make subroutine call
        self.compile_subroutine_call(next_token)

        # Verify end of statement
        self.verify_token(";")
        
        # Pop return value off stack
        self.writer.write_pop("temp", 0)

    def compile_let(self):
        contains_array = False

        # Let keyword
        self.verify_token("let")

        # Variable name
        current_var = self.type()
        current_var_kind = current_var.split(".")[1]
        current_var_index = current_var.split(".")[4]
        if "field" in current_var_kind:
            current_var_kind = "this"
        elif "var" in current_var_kind:
            current_var_kind = "local"
        
        self.advance_token()
        
        # Check for array
        if self.token() == "[":
            contains_array = True
            self.writer.write_push(current_var_kind, current_var_index)
            current_var_kind = "that"
            current_var_index = 0

            self.verify_token("[")
            self.compile_expression()
            self.verify_token("]")

            self.writer.write_artihmetic("add")
        
        self.verify_token("=")

        # Check for method call
        current_token_type = self.type().split(".")
        if len(current_token_type) > 4:
            current_index = current_token_type[4]
            current_segment = current_token_type[1]
            self.tokenizer.advance()
            next_token = self.token()
            self.tokenizer.reverse()
            if current_segment == "field" and self.is_method and next_token == ".": 
                self.writer.write_push("this", current_index)

        self.compile_expression()
        self.verify_token(";")

        if contains_array:
            self.writer.write_pop("temp", 0)
            self.writer.write_pop("pointer", 1)
            self.writer.write_push("temp", 0)
        self.writer.write_pop(current_var_kind, current_var_index)

    def compile_while(self):
        label_one,label_two = self.create_label(), self.create_label()
        
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

        # Check if return statement is expressionless
        if self.token() == ";":
            self.verify_token(";")
            if is_void:
                self.writer.write_push("constant", 0)
            if self.is_constructor:
                self.is_constructor = False
            self.writer.write_return()
        # Compile expression in return statement
        else:
            self.compile_expression()
            if self.is_constructor:
                self.is_constructor = False
            self.writer.write_return()
            self.advance_token()

    def compile_if(self):
        label_one,label_two, label_three = self.create_label(), self.create_label(), self.create_label()

        self.verify_token("if")
        self.verify_token("(")
        self.compile_expression()
        self.verify_token(")")

        self.writer.write_if(label_one)
        self.writer.write_goto(label_two)
        self.writer.write_label(label_one)

        self.verify_token("{")
        self.compile_statements()
        self.verify_token("}")

        if self.token() == "else":
            self.writer.write_goto(label_three)
            self.writer.write_label(label_two)
            self.verify_token("else")
            self.verify_token("{")
            self.compile_statements()
            self.verify_token("}")
            self.writer.write_label(label_three)
        else:
            self.writer.write_label(label_two) 

    def create_label(self):
        label = "L{}".format(self.label_count)
        self.label_count += 1
        return label

    def compile_expression(self):
        self.compile_term()
        while self.is_op():
            current_op = self.token()
            self.advance_token()
            self.compile_term()
            self.write_op(current_op)

    def compile_term(self):
        current_token = self.token()
        current_token_type = self.type()
        keyword_constants = ["this"]
        
        if current_token_type == "integerConstant":
            self.writer.write_push("constant", current_token)
            if self.negative_term:
                self.writer.write_artihmetic("neg")
            self.negative_term = False
            self.advance_token()
        elif current_token_type == "stringConstant":
            # Get length of string (excluse quotation marks)
            string_length = len(current_token) - 2
            self.writer.write_push("constant", string_length) 
            # Construct new string
            self.writer.write_call("String.new", 1)
            # Build new string
            for letter in current_token:
                unicode_code = ord(letter)
                # Excluse quotation marks
                if unicode_code != 34:
                    self.writer.write_push("constant", unicode_code)
                    self.writer.write_call("String.appendChar", 2)
            self.advance_token()
        elif current_token in keyword_constants:
            self.writer.write_push("pointer", 0)
            self.advance_token()
        elif current_token == "true":
            self.writer.write_push("constant", 1)
            self.writer.write_artihmetic("neg")
            self.advance_token()
        elif current_token == "false" or current_token == "null":
            self.writer.write_push("constant", 0)
            self.advance_token()
        elif current_token == "(":
            self.verify_token("(")
            self.compile_expression()
            self.verify_token(")")
        elif current_token == "~":
            self.advance_token()
            self.compile_term()
            self.writer.write_artihmetic("not")
        elif current_token == "-":
            self.reverse_token()
            previous_token = self.token()
            self.advance_token()

            if previous_token in [",", "(", "="]:
                self.negative_term = True
            
            self.advance_token()
            self.compile_term()

        elif "identifier" in current_token_type:
            def assign_and_push():
                identifier_parts = self.type().split(".")
                if identifier_parts[1] == "var":
                    identifier_parts[1] = "local"
                if identifier_parts[1] == "field":
                    identifier_parts[1] = "this"

                self.writer.write_push(identifier_parts[1], identifier_parts[4])

            self.tokenizer.advance()
            next_token = self.token()
            self.tokenizer.reverse()

            if next_token == "[":
                assign_and_push()
                self.advance_token()

                self.verify_token("[")
                self.compile_expression()
                self.verify_token("]")

                self.writer.write_artihmetic("add")
                self.writer.write_pop("pointer", 1)
                self.writer.write_push("that", 0)
            elif next_token == "(" or next_token == ".":
                self.compile_subroutine_call(next_token)
            else:
                assign_and_push()
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
        elif op_symbol == "/":
            self.writer.write_call("Math.divide", 2)
        else:
            raise Exception("Operation {} not recognized.".format(op_symbol))

    
    def compile_subroutine_call(self, token):
        # Class/Variable name
        name_token = self.token()
        total_arguments = 0
        if token == "(":
            self.advance_token()
            self.verify_token("(")
            total_arguments += self.compile_expression_list()
            self.verify_token(")")
            self.writer.write_call("{}.{}".format(self.class_name, name_token), total_arguments + 1)
        elif token == ".":
            # Check if type exists
            identifier_parts = self.type().split(".")
            if len(identifier_parts) > 5: # Includes type
                name_token = identifier_parts[5]
                total_arguments += 1
               
            self.advance_token()
            # . symbol
            self.verify_token(".")
            # Subroutine name
            subroutine_name = self.token()
            self.advance_token()
            # ( symbol
            self.verify_token("(")
            # Expression list
            total_arguments += self.compile_expression_list()
            # ) symbol
            self.verify_token(")")
            self.writer.write_call("{}.{}".format(name_token, subroutine_name), total_arguments)
        else:
            raise Exception("Incorrect syntax for subroutine call.")

    def is_op(self):
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        if self.token() in ops:
            return True
        return False

    def compile_expression_list(self):
        total_arguments = 0
        if self.is_expression():
            total_arguments += 1
            self.compile_expression()
            while self.token() == ",":
                self.advance_token()
                total_arguments += 1
                self.compile_expression()
        return total_arguments
    
    def is_expression(self):
        constants = ["integerConstant", "stringConstant"]
        token_type = self.type()
        symbols = ["(", "~", "-"]
        if token_type in constants or "identifier" in token_type or "keyword" in token_type or self.token() in symbols:
            return True
        return False

    def get_previous_token(self):
        self.tokenizer.reverse()
        previous_token = self.token()
        self.tokenizer.advance()
        return previous_token