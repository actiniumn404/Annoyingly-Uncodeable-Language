import string
from errors import *


class Compile:
    def __init__(self, code):
        self.source = code
        self.curPos = 0
        self.curChar = ""
        self.location = None
        self.clipboard = None
        self.valid = list(string.whitespace) + ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] + list(string.ascii_lowercase) + ["\0", "", "\n", "!", "#", "*", "+", "/", "-", "$"]
        self.memory = ""
        self.memory_state = "end"
        self.out = print
        self.variables = {}
        self.valid_data_types = ["integer", "string", "float", "function"]
        self.parse(self.source)

    def next_char(self, source):
        if self.curPos >= len(source):
            # End of Line
            self.curChar = "\0"
            return
        self.curChar = source[self.curPos]
        self.curPos += 1

    def peek(self, source):
        if self.curPos + 1 >= len(source):
            # End of Program
            return "\0"
        return source[self.curPos]

    def parse(self, source):
        self.memory_state = "end"
        while self.curChar != "\0":
            # Comments
            if self.curChar == "#":
                while self.curChar != "\n" and self.curChar != "\0":
                    self.next_char(source)
            # "INput"
            if self.curChar == "i":
                self.next_char(source)
                if self.curChar == "n":
                    if self.memory_state == "start":
                        user_input = input()
                        self.memory += user_input
            # Memory Clear
            if self.curChar == "m":
                if self.peek(source) == "c":
                    self.memory = ""
                    self.next_char(source)


            # Variables
            if self.curChar == "$":
                self.next_char(source)
                name = ""
                while self.curChar not in [" ", "\n", "\0"]:
                    name += self.curChar
                    self.next_char(source)
                self.next_char(source)
                if (source[self.curPos - 1:min(self.curPos + 2, len(source) - 1)]).isalpha():
                    data_type = ""
                    while self.curChar not in [" ", "\n", "\0"]:
                        data_type += self.curChar
                        self.next_char(source)
                    if data_type not in self.valid_data_types:
                        raise InvalidDataType(data_type)
                    elif data_type != "function":
                        self.variables[name] = variable(name, data_type, str(self.memory))
                    else:
                        # move the pointer past the space
                        self.next_char(source)
                        # take care of the parameters
                        parameters = ""
                        while self.curChar not in [" ", "\n", "\0"]:
                            parameters += self.curChar
                            self.next_char(source)
                        function_content = ""
                        while source[self.curPos - 8:self.curPos - 1] != "endfunc":
                            function_content += self.curChar
                            self.next_char(source)
                        function_content = function_content[:-8]
                else:
                    if self.memory_state == "start":
                        self.memory += str(self.variables[name].content)

            # "Commands"
            if self.curChar == "!":
                self.next_char(source)
                # Copy
                if self.curChar == "c":
                    self.clipboard = self.memory

                # Paste
                elif self.curChar == "v":
                    if not self.clipboard:
                        raise EmptyClipboard(source, self.curPos)
                    else:
                        self.memory = self.clipboard

                # Print
                elif self.curChar == "p":
                    if self.memory and self.memory_state == "end":
                        self.out(self.memory)

                # Mathematical Computations
                elif source[self.curPos - 1:self.curPos + 3] == "math":
                    for _ in range(5):
                        self.next_char(source)
                    operand1 = ""
                    operand2 = ""
                    if self.curChar != "$":
                        while self.curChar in ["c", "v"]:
                            operand1 += {"c": "0", "v": "1"}.get(self.curChar)
                            self.next_char(source)
                    else:
                        while self.curChar not in ["+", "-", "*", "/"]:
                            operand1 += self.curChar
                            self.next_char(source)
                    operation = self.curChar
                    self.next_char(source)
                    if self.curChar != "$":
                        while self.curChar in ["c", "v"]:
                            operand2 += {"c": "0", "v": "1"}.get(self.curChar)
                            self.next_char(source)
                    else:
                        while self.curChar not in ["\0", "\n", " ", "!"]:
                            operand2 += self.curChar
                            self.next_char(source)
                        self.next_char(source)
                    if operand1[0] == "$":
                        operand1 = self.variables.get(operand1[1:]).content
                    else:
                        operand1 = int(operand1, 2)
                    if operand2[0] == "$":
                        operand2 = self.variables.get(operand2[1:]).content
                    else:
                        operand2 = int(operand2, 2)
                    if operation == "+":
                        result = operand1 + operand2
                    if operation == "-":
                        result = operand1 - operand2
                    if operation == "*":
                        result = operand1 * operand2
                    if operation == "/":
                        result = operand1 / operand2
                    if self.memory_state == "start":
                        self.curPos -= 2
                        self.curChar = self.source[self.curPos]
                        #print(operand1, operand2, operation, result, self.curChar, self.curPos)
                        self.memory += str(result)
                # Memory (start/end)
                elif self.curChar == "m":
                    before = self.memory_state[:]
                    if before == "end":
                        self.memory_state = "start"
                        # self.memory = ""
                    else:
                        self.memory_state = "end"
                    #print(self.memory_state, self.curChar)
                # User created functions
                else:
                    pass
                self.next_char(source)

            # For loop
            if source[self.curPos - 5:self.curPos - 1] == "loop":
                self.next_char(source)
                loop_from = ""
                loop_to = ""
                while self.curChar not in ["-", " ", "\n", "\0"]:
                    loop_from += self.curChar
                    self.next_char(source)
                self.next_char(source)
                while self.curChar not in ["-", " ", "\n", "\0"]:
                    loop_to += self.curChar
                    self.next_char(source)

                if loop_from[0] == "$":
                    loop_from = int(self.variables[loop_from[1:]].content)
                else:
                    loop_from = int(loop_from.replace("c", "0").replace("v", "1"), 2)
                if loop_to[0] == "$":
                    loop_to = int(self.variables[loop_to[1:]].content)
                else:
                    loop_to = int(loop_to.replace("c", "0").replace("v", "1"), 2)
                for _ in range(5):
                    self.next_char(source)
                loop_variable = ""
                while self.curChar not in [" ", "\n", "\0"]:
                    loop_variable += self.curChar
                    self.next_char(source)
                loop_end = 1
                loop_content = ""
                while loop_end:
                    if source[self.curPos - 7:self.curPos] == "endloop":
                        loop_end = loop_end - 1
                    elif source[self.curPos - 5:self.curPos - 1] == "loop":
                        loop_end += 1
                    loop_content += self.curChar
                    self.next_char(source)
                loop_content = loop_content[:-8].strip("\n")
                myPos = self.curPos
                for looper in range(loop_from, loop_to):
                    self.variables[loop_variable] = variable(loop_variable, "integer", looper)
                    self.memory = ""
                    self.curChar = ""
                    self.memory_state = "end"
                    self.curPos = 0
                    self.parse(loop_content)
                self.curPos = myPos
                self.curChar = self.source[self.curPos - 1]

            # plain text
            elif self.curChar in ["c", "v"]:
                binary = ""
                while self.curChar in ["c", "v"]:
                    binary += {"c": "0", "v": "1"}.get(self.curChar)
                    self.next_char(source)
                if self.memory_state == "start":
                    self.memory += chr(int(binary, 2))

            elif self.curChar == ">":
                self.next_char(source)
                self.next_char(source)
                file_name = ""
                binary = ""
                while self.curChar in [" ", "c", "v", "\n"]:
                    if self.curChar == " " or self.curChar == "\n":
                        try:
                            file_name += chr(int(binary, 2))
                            binary = ""
                        except ValueError:
                            pass
                    else:
                        binary += {"c": "0", "v": "1"}.get(self.curChar, "")
                    self.next_char(source)
                self.out = open(file_name, "w").write

            elif self.curChar in self.valid:
                self.next_char(source)
            else:
                raise UnexpectedCharacter(source, self.curPos)




class variable:
    def __init__(self, name, data_type, content, parameters=None, function_content=None):
        self.name = name
        self.data_type = data_type
        self.parameters = parameters
        self.content = content
        self.function_content = function_content
        # get the data type parse function
        self.data_type_function = {"string": str, "integer": int, "float": float, "function": do_nothing}[
            self.data_type]
        try:
            self.content = self.data_type_function(str(self.content))
        except BaseException:
            raise SegmentationFault(f"The value of variable \"{self.name}\" is not a valid \"{self.data_type}\" object")



def do_nothing(*args):
    return ",".join(args)
