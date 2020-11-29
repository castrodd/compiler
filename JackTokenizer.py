from JackToken import *
from SymbolTable import SymbolTable

class JackTokenizer:
    def __init__(self, filename):
        self.symbols = frozenset(['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', 
                                 '*', '/', '&', '|', '<', '>', '=', '~'])
        self.keywords = frozenset(['class', 'constructor', 'function', 'method', 'field', 'static',
                                  'var', 'int', 'char', 'boolean', 'void', 'true', 'false',
                                  'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'])
        self.integers = '1234567890'
        self.jack_standard_library = ['Math', 'String', 'Array', 'Output', 'Screen', 'Keyboard', 'Memory', 'Sys']

        self.tokens = list()
        self.symbol_table = SymbolTable()
        self.tokenize_stream(filename)
        self.add_extended_identifiers()
        for t in self.tokens:
            print(t.get_token(), t.get_token_type())
        self.current_index = 0

    def tokenize_stream(self, file):
        with open(file) as f:
           all_lines = list(f)
           clean_lines = self.remove_single_line_comments(all_lines)
           parsed_lines = self.parse_lines(clean_lines)
           self.parse_tokens(parsed_lines)

    def remove_single_line_comments(self, f):
        all_lines = list(f)
        clean_lines = list()
        for line in all_lines:
            no_newline = line.strip()
            no_single_line_comments = no_newline.partition("//")[0]
            filtered_lines = filter(lambda x: x != '', no_single_line_comments)
            clean_lines += filtered_lines
        return clean_lines

    def parse_lines(self, lines):
        raw_tokens = list()
        current_stream = ""
        multiline_comment = False
        string_const = False

        for index, char in enumerate(lines):
            if char == "/" and len(lines) > index + 2 and lines[index+1] == "*" and lines[index+2 == "*"]:
                multiline_comment = True
            elif char == "/" and index > 0 and lines[index-1] == "*":
                multiline_comment = False
            elif not multiline_comment:
                if char in self.symbols:
                    if current_stream != "":
                        raw_tokens.append(current_stream)
                    raw_tokens.append(char)
                    current_stream = ""
                elif char == " " and not string_const:
                    if current_stream != "":
                        raw_tokens.append(current_stream)
                    current_stream = ""
                elif char == "\"" and not string_const:
                    string_const = True
                    current_stream += char
                elif char == "\"" and string_const:
                    string_const = False
                    current_stream += char
                else:
                    current_stream += char

        if current_stream != "":
            raw_tokens.append(current_stream)
        return raw_tokens

    def parse_tokens(self, tokens):
        for token in tokens:
            if len(token) == 1:
                if token in self.symbols:
                    current_token = JackToken(token, "symbol")
                    self.tokens.append(current_token)
                elif token in self.integers:
                    current_token = JackToken(token, "integerConstant")
                    self.tokens.append(current_token)
                else:
                    current_token = JackToken(token, "identifier")
                    self.tokens.append(current_token)
            else:
                if token in self.keywords:
                    current_token = JackToken(token, "keyword")
                    self.tokens.append(current_token)
                elif token[0] == "\"":
                    current_token = JackToken(token, "stringConstant")
                    self.tokens.append(current_token)
                elif token[0] in self.integers:
                    current_token = JackToken(token, "integerConstant")
                    self.tokens.append(current_token)
                else:
                    current_token = JackToken(token, "identifier")
                    self.tokens.append(current_token)
        return self.tokens

    def add_extended_identifiers(self):
        for current_index in range(0, len(self.tokens)):
            current_token = self.tokens[current_index]
            token_name = current_token.get_token()
            token_type = current_token.get_token_type()

            if token_type == "identifier":
                type_index = current_index - 1
                kind_index = current_index - 2

                if type_index >= 0:
                    type_token = self.tokens[type_index].get_token()
                else:
                    type_token = None

                if kind_index >= 0:
                   kind_token = self.tokens[kind_index].get_token()
                else:
                    kind_token = None

                def add_to_symbol_table(kind):
                    identifier_type = type_token
                    self.symbol_table.define(token_name, identifier_type, kind)

                # Class
                if type_token == "class":
                    self.symbol_table.set_class_name(token_name)
                    current_token.set_token_type("identifier.class.defined.false.0")
                # Subroutine
                elif kind_token in ["constructor", "function", "method"]:
                    self.symbol_table.start_subroutine()
                    if kind_token == "method":
                        self.symbol_table.define("this", self.symbol_table.get_class(), "argument")
                    current_token.set_token_type("identifier.subroutine.defined.false.0")
                # Arg
                elif kind_token in ["(", ","]:
                    add_to_symbol_table("argument")
                    running_index = self.symbol_table.var_count("argument")
                    current_token.set_token_type("identifier.argument.used.true.{}".format(running_index))
                # Var
                elif kind_token == "var":
                    add_to_symbol_table("var")
                    running_index = self.symbol_table.var_count("var")
                    current_token.set_token_type("identifier.var.defined.true.{}".format(running_index))
                # Static
                elif kind_token == "static":
                    add_to_symbol_table("static")
                    running_index = self.symbol_table.var_count("static")
                    current_token.set_token_type("identifier.static.defined.true.{}".format(running_index))
                # Field
                elif kind_token == "field":
                    add_to_symbol_table("field")
                    running_index = self.symbol_table.var_count("field")
                    current_token.set_token_type("identifier.field.defined.true.{}".format(running_index))
                # Identifier in list (e.g. var int i, j, k, etc.)
                elif type_token == ",":
                    kind_token = None
                    temp_index = type_index
                    while (not kind_token) and (temp_index > 0):
                        temp_index = temp_index - 1
                        temp_token = self.tokens[temp_index].get_token()
                        if temp_token in ["field", "static", "var"]:
                            self.symbol_table.define(token_name, self.tokens[temp_index + 1].get_token(), temp_token)
                            running_index = self.symbol_table.var_count(temp_token)
                            current_token.set_token_type("identifier.{}.defined.true.{}".format(temp_token, running_index))
                # Abstract data types
                elif type_token in ["field", "static", "var"]:
                    current_token.set_token_type("identifier.class.used.false.0")
                # Identifiers already in symbol table
                elif self.symbol_table.get_symbol(token_name):
                    running_index = self.symbol_table.index_of(token_name)
                    token_type = self.symbol_table.kind_of(token_name)
                    current_token.set_token_type("identifier.{}.used.true.{}".format(token_type, running_index))
                # Identifier is the class itself
                elif token_name == self.symbol_table.get_class():
                    current_token.set_token_type("identifier.class.used.0")
                # Jack Standard Library
                elif token_name in self.jack_standard_library:
                    current_token.set_token_type("identifier.class.used.false.0")
                # Method calls
                elif type_token == ".":
                    current_token.set_token_type("identifier.subroutine.used.false.0")
                else:
                    raise Exception("Identifier type {} and kind {} not found for {}.".format(type_token, kind_token, token_name))

    def hasMoreTokens(self):
        if self.current_index < len(self.tokens) - 1:
            return True
        else:
            return False

    def advance(self):
        self.current_index += 1

    def reverse(self):
        self.current_index -= 1

    def token_type(self):
        current_token = self.tokens[self.current_index]
        return current_token.get_token_type()

    def token(self):
        current_token = self.tokens[self.current_index]
        return current_token.get_token()

    