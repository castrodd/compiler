from JackToken import *

class JackTokenizer:
    def __init__(self, filename):
        self.symbols = frozenset(['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', 
                                 '*', '/', '&', '|', '<', '>', '=', '~'])
        self.keywords = frozenset(['class', 'constructor', 'function', 'method', 'field', 'static',
                                  'var', 'int', 'char', 'boolean', 'void', 'true', 'false',
                                  'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'])
        self.integers = '1234567890'

        self.tokens = list()
        self.tokenize_stream(filename)
        #self.output_tokens(filename)
        self.current_index = 0

    def tokenize_stream(self, file):
        with open(file) as f:
           all_lines = list(f)
           clean_lines = self.remove_single_line_comments(all_lines)
           parsed_lines = self.parse_lines(clean_lines)
           self.parse_tokens(parsed_lines)
    
    # def output_tokens(self, filename):
    #     currentFileName = filename.partition(".")[0]
    #     outputFileName = currentFileName + "T.xml"
    #     outputFile = open(outputFileName, 'a+')

    #     outputFile.write("<tokens>\n")
    #     for token in self.tokens:
    #         tokenType = token.get_token_type()
    #         token = token.get_token()
    #         if tokenType == "stringConstant":
    #             token = token[1:-1] # Strip quotation marks
    #         if token == "<":
    #             token = "&lt;"
    #         if token == ">":
    #             token = "&gt;"
    #         if token == "&":
    #             token = "&amp;" 
    #         outputFile.write("\t<{tType}> {t} </{tType}>\n".format(tType=tokenType, t=token))
    #     outputFile.write("</tokens>")


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

    def hasMoreTokens(self):
        if self.current_index < len(self.tokens) - 1:
            return True
        else:
            return False

    def advance(self):
        self.current_index += 1

    def token_type(self):
        current_token = self.tokens[self.current_index]
        return current_token.get_token_type()

    def token(self):
        current_token = self.tokens[self.current_index]
        return current_token.get_token()

    