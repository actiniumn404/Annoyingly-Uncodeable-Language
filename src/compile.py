# The official Annoyingly Uncodeable Language (AUL) Compiler
# By Andrew Chen (actiniumn404 on GitHub)
# Licensed under the GNU GPLv3 License

import string
from errors import *
import pathlib


class Compile:
    def __init__(self, code):
        self.source = code
        self.curPos = 0
        self.curChar = ""
        self.location = None
        self.clipboard = None
        self.valid = list(string.whitespace) + ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] + list(
            string.ascii_lowercase) + ["\0", "", "\n", "!", "#", "*", "+", "/", "-", "$", "?", "<", ">", "=", "|", ]
        self.memory = ""
        self.memory_state = "end"
        self.out = print
        self.variables = {"__name__": Variable("__name__", "string", "__main__")}
        self.valid_data_types = ["integer", "string", "float", "function", "bool", "array"]
        self.mailbox = ""

        # set up path for importing
        self.file_path = str(pathlib.Path(__file__).parent.resolve())

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

    def booleen(self, test_string: str):
        test_string = test_string.strip()
        valid = [
            "+",  # and
            "|",  # or
            "x",  # not
            "in",  # in
            "xin",  # x-in = not in
            "=",  # equals
            "x=",  # x= = not equal
            ">",  # greater than
            "<",  # less than
            "<=",  # less than equal to
            ">=",  # greater than equal to
        ]
        parts = test_string.split(" ")
        pointer = 0
        op1 = ""
        for index in range(len(parts)):
            part = parts[index]
            if part[0] == "$":
                parts[index] = self.variables[part[1:]].content
            elif part == "Yes":
                parts[index] = True
            elif part == "No":
                parts[index] = False
        while pointer < len(parts):
            part = parts[pointer]
            # assume is a variable if not one of the above
            if part not in valid:
                op1 = part
                pointer += 1
                continue
            # now onto the ops
            if part == "+":  # and
                pointer += 1
                next_p = parts[pointer]
                op1 = bool(next_p and op1)
            elif part == "|":  # or
                pointer += 1
                next_p = parts[pointer]
                op1 = bool(next_p or op1)
            elif part == "x":  # not
                op1 = not op1
            elif part == "in":  # if {variable} in {string}
                pointer += 1
                next_p = parts[pointer]
                op1 = op1 in next_p
            elif part == "xin":  # not in: if {variable} xin {string}
                pointer += 1
                next_p = parts[pointer]
                op1 = op1 not in next_p
            elif part == "=":  # equal to
                pointer += 1
                next_p = parts[pointer]
                op1 = bool(op1 == next_p)
            elif part == "x=":  # not equal to
                pointer += 1
                next_p = parts[pointer]
                op1 = bool(op1 != next_p)
            elif part == ">":
                pointer += 1
                next_p = parts[pointer]
                op1 = bool(op1 > next_p)
            elif part == "<":
                pointer += 1
                next_p = parts[pointer]
                op1 = bool(op1 < next_p)
            elif part == ">=":
                pointer += 1
                next_p = parts[pointer]
                op1 = bool(op1 >= next_p)
            elif part == "<=":
                pointer += 1
                next_p = parts[pointer]
                op1 = bool(op1 <= next_p)

            pointer += 1
        return bool(op1)

    def parse(self, source, notes="", variable_name_prefix=""):
        self.memory_state = "end"
        while self.curChar != "\0":
            # continue for loops
            if self.mailbox == "continue" and notes == "in loop":
                return

            # Comments
            if self.curChar == "#":
                while self.curChar != "\n" and self.curChar != "\0":
                    self.next_char(source)
            # "INput"
            if self.curChar == "i":
                self.next_char(source)
                if self.curChar == "n":
                    if self.memory_state == "start":
                        user_input = input(">? ")
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
                while self.curChar not in [" ", "\n", "\0", "#"]:
                    name += self.curChar
                    self.next_char(source)
                name = variable_name_prefix+name
                self.next_char(source)
                if (source[self.curPos - 1:min(self.curPos + 2, len(source) - 1)]).isalpha():
                    data_type = ""
                    while self.curChar not in [" ", "\n", "\0", "#"]:
                        data_type += self.curChar
                        self.next_char(source)
                    if data_type not in self.valid_data_types:
                        raise InvalidDataType(data_type)
                    elif data_type != "function":
                        self.variables[name] = Variable(name, data_type, str(self.memory))
                    else:
                        # move the pointer past the space
                        self.next_char(source)
                        # take care of the parameters
                        parameters = ""
                        while self.curChar not in ["\n", "\0", "#"]:
                            parameters += self.curChar
                            self.next_char(source)
                        function_content = ""
                        while source[self.curPos - 8:self.curPos - 1] != "endfunc":
                            function_content += self.curChar
                            self.next_char(source)
                            if self.curChar == "\0":
                                raise EndOfProgramError("Expected \"endfunc\" before the end of program")
                        function_content = function_content[:-8]
                        self.variables[name] = Variable(name, "function", function_content, parameters)
                else:
                    if self.memory_state == "start":
                        self.memory += str(self.variables[name].content)

            # "Commands"
            if self.curChar == "!":
                self.next_char(source)

                # python sys
                if source[self.curPos - 1:self.curPos + 2] == "sys":
                    for _ in range(4):
                        self.next_char(source)
                    sys_content = ""
                    while self.curChar not in ["\0", "\n", "#"]:
                        sys_content += self.curChar
                        self.next_char(source)
                    sys_content = self.variables[sys_content[1:]].content
                    if self.memory_state == "start":
                        exec(sys_content)

                # Copy
                elif self.curChar == "c":
                    self.clipboard = self.memory

                # Paste
                elif self.curChar == "v":
                    if not self.clipboard:
                        raise EmptyClipboard(source, self.curPos)
                    else:
                        self.memory += self.clipboard

                # Print
                elif self.curChar == "p":
                    if self.memory:
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
                        while self.curChar not in ["\0", "\n", " ", "!", "#"]:
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
                        self.curPos -= 1
                        self.curChar = source[self.curPos]
                        self.memory += str(result)
                # Memory (start/end)
                elif self.curChar == "m":
                    before = self.memory_state[:]
                    if before == "end":
                        self.memory_state = "start"
                        # self.memory = ""
                    else:
                        self.memory_state = "end"
                # Booleens
                elif self.curChar == "b":
                    test_string = ""
                    self.next_char(source)
                    self.next_char(source)
                    while self.curChar not in ["!", "\0", "\n", "#"]:
                        test_string += self.curChar
                        self.next_char(source)
                    if self.memory_state == "start":
                        self.memory += str(self.booleen(test_string))
                    self.curPos -= 1
                    self.curChar = source[self.curPos]
                # User created functions
                else:
                    func_name = ""
                    while self.curChar not in [" ", "\n", "\0", "#"]:
                        func_name += self.curChar
                        self.next_char(source)
                    function_object = self.variables[func_name]
                    parameters = ""
                    while self.curChar not in ["\n", "\0", "#"]:
                        parameters += self.curChar
                        self.next_char(source)
                    parameters = parameters.strip().split(" ")
                    # Some syntax error checks
                    if len(parameters) != len(function_object.parameters):
                        raise TypeError(f"Expected {len(function_object.parameters)} parameters, got {len(parameters)}")
                    if not all([x[0] == "$" for x in parameters]):
                        raise SyntaxError("Function parameters must be variables")
                    for i in range(len(parameters)):
                        self.variables[function_object.parameters[i].name] = Variable(
                            function_object.parameters[i].name,
                            function_object.parameters[i].data_type,
                            self.variables[parameters[i][1:]].content)
                    myPos = self.curPos
                    self.memory = ""
                    self.curChar = ""
                    self.memory_state = "end"
                    self.curPos = 0
                    # == Run Function Code ==
                    self.parse(function_object.content, "in function", variable_name_prefix)
                    # == End Run ==
                    self.curPos = myPos
                    self.curChar = source[self.curPos - 1]

                self.next_char(source)

            # For loop
            if source[self.curPos - 5:self.curPos - 1] == "loop":
                self.next_char(source)
                loop_from = ""
                loop_to = ""
                while self.curChar not in ["-", " ", "\n", "\0", "#"]:
                    loop_from += self.curChar
                    self.next_char(source)
                self.next_char(source)
                while self.curChar not in ["-", " ", "\n", "\0", "#"]:
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
                while self.curChar not in [" ", "\n", "\0", "#"]:
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
                    self.variables[loop_variable] = Variable(loop_variable, "integer", looper)
                    self.memory = ""
                    self.curChar = ""
                    self.memory_state = "end"
                    self.curPos = 0
                    self.parse(loop_content, "in loop", variable_name_prefix)
                    if self.mailbox != "":
                        if self.mailbox == "break":
                            break
                        self.mailbox = ""
                self.curPos = myPos
                self.curChar = source[self.curPos - 1]

            # while loop
            elif source[self.curPos - 1:self.curPos + 4] == "wloop":
                # Move the pointer past the keyword and the whitespace
                for _ in range(6):
                    self.next_char(source)
                test_bool = ""
                while self.curChar != "\n":
                    test_bool += self.curChar
                    self.next_char(source)
                self.next_char(source)
                # Take the content of the loop
                loop_end = 1
                loop_content = ""
                while loop_end:
                    if source[self.curPos - 1:self.curPos + 8] == "endwhloop":
                        loop_end = loop_end - 1
                    elif source[self.curPos - 1:self.curPos + 4] == "wloop":
                        loop_end += 1
                    loop_content += self.curChar
                    self.next_char(source)
                    if self.curChar == "\0":
                        raise EndOfProgramError("Expected \"endwhloop\" before the end of program")
                loop_content = loop_content[:-1].strip(" \n")
                myPos = self.curPos
                while self.booleen(test_bool):
                    self.memory = ""
                    self.curChar = ""
                    self.memory_state = "end"
                    self.curPos = 0
                    self.parse(loop_content, "in loop", variable_name_prefix)
                    if self.mailbox != "":
                        if self.mailbox == "break":
                            break
                        self.mailbox = ""
                self.curPos = myPos
                self.curChar = source[self.curPos - 1]

            # plain text
            elif self.curChar in ["c", "v"]:
                binary = ""
                while self.curChar in ["c", "v"]:
                    binary += {"c": "0", "v": "1"}.get(self.curChar)
                    self.next_char(source)
                if self.memory_state == "start":
                    self.memory += chr(int(binary, 2)).replace(chr(0), "")
            # If/Else
            elif source[self.curPos - 1:self.curPos + 2] == "?if":
                self.next_char(source)
                self.next_char(source)
                self.next_char(source)
                self.next_char(source)

                test_bool = ""
                while self.curChar not in ["\n", "\0"]:
                    test_bool += self.curChar
                    self.next_char(source)
                num_ifs = 1
                if_content = ""
                self.next_char(source)
                while num_ifs and self.curChar != "\0":
                    if source[self.curPos - 1:self.curPos + 2] == "?if":
                        num_ifs += 1
                    elif source[self.curPos - 1:self.curPos + 5] == "end?if":
                        num_ifs -= 1
                    if_content += self.curChar
                    self.next_char(source)
                    if self.curChar == "\0":
                        raise EndOfProgramError("Expected \"end?if\" before the end of program")
                if_content = if_content[:-1].strip("\n ")
                test_bool = self.booleen(test_bool)
                if test_bool:
                    myPos = self.curPos
                    self.memory = ""
                    self.curChar = ""
                    self.memory_state = "end"
                    self.curPos = 0
                    # == Start Run ==
                    self.parse(if_content, notes, variable_name_prefix)
                    # == End Run ==
                    self.curPos = myPos
                    self.curChar = source[self.curPos - 1]
                for _ in range(5):
                    self.next_char(source)
                # Take care of else loop
                while self.curChar in [" ", "\n"]:
                    self.next_char(source)
                if source[self.curPos - 1:self.curPos + 4] == "?else":
                    # Move the pointer past the keyword
                    for _ in range(5):
                        self.next_char(source)
                    num_else = 1
                    else_content = ""
                    self.next_char(source)
                    while num_else and self.curChar != "\0":
                        if source[self.curPos - 1:self.curPos + 4] == "?else":
                            num_else += 1
                        elif source[self.curPos - 1:self.curPos + 7] == "end?else":
                            num_else -= 1
                        else_content += self.curChar
                        self.next_char(source)
                        if self.curChar == "\0":
                            raise EndOfProgramError("Expected \"end?else\" before the end of program")
                    else_content = else_content[:-1].strip(" \n")
                    for _ in range(8):
                        self.next_char(source)
                    if not test_bool:
                        myPos = self.curPos
                        self.memory = ""
                        self.curChar = ""
                        self.memory_state = "end"
                        self.curPos = 0
                        # == Start Run ==
                        self.parse(else_content, notes, variable_name_prefix)
                        # == End Run ==
                        self.curPos = myPos
                        self.curChar = source[self.curPos - 1]

            elif self.curChar == ">":
                self.next_char(source)
                self.next_char(source)
                file_name = ""
                binary = ""
                while self.curChar in [" ", "c", "v", "\n", "#"]:
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

            elif self.curChar == "+":
                self.next_char(source)
                self.next_char(source)
                filename = ""
                while self.curChar not in ["\0", "#", "\n"]:
                    filename += self.curChar
                    self.next_char(source)

                filename = "".join(
                    list(map(lambda part: chr(int(part.replace("v", "1").replace("c", "0"), 2)), filename.split(" "))))
                file_content = ""
                for test_case in [filename, filename + ".aul", self.file_path + "/" + filename,
                                  self.file_path + "/" + filename + ".aul", self.file_path + filename,
                                  self.file_path + filename + ".aul", self.file_path + "/built-in/" + filename + ".aul",
                                  self.file_path + "/built-in" + filename + ".aul",
                                  self.file_path + "/built-in" + filename, self.file_path + "/built-in/" + filename]:
                    try:
                        file_content = open(test_case, "r").read()
                    except BaseException:
                        continue
                    break
                myPos = self.curPos
                self.memory = ""
                self.curChar = ""
                self.memory_state = "end"
                self.curPos = 0
                self.variables["__name__"] = Variable("__name__", "string", "__import__")
                # == Start Run ==
                self.parse(file_content, filename+".")
                # == End Run ==
                self.variables["__name__"] = Variable("__name__", "string", "__main__")
                self.curPos = myPos
                self.curChar = source[self.curPos - 1]

            # break/continue statements for loops
            elif source[self.curPos - 1:self.curPos + 4] == "break":
                if notes != "in loop":
                    raise SyntaxError("Illegal break statement")
                self.mailbox = "break"
                return
            elif source[self.curPos - 1:self.curPos + 5] == "nextit":
                if notes != "in loop":
                    raise SyntaxError("Illegal nextit (continue) statement")
                self.mailbox = "continue"
                return

            elif self.curChar in self.valid:
                self.next_char(source)
            else:
                raise UnexpectedCharacter(source, self.curPos)


class Variable:
    def __init__(self, name: str, data_type: str, content: str, parameters=None):
        if data_type not in ["string", "integer", "float", "function", "bool", "array"]:
            raise InvalidDataType(data_type)
        self.name = name
        self.data_type = data_type
        self.parameters = parameters
        self.content = content
        # get the data type parse function
        self.data_type_function = {"string": str, "integer": int, "float": float, "function": self.do_nothing,
                                   "bool": lambda b: True if b == "True" else False, "array":list}[
            self.data_type]
        try:
            self.content = self.data_type_function(str(self.content))
        except BaseException:
            raise SegmentationFault(f"The value of variable \"{self.name}\" is not a valid \"{self.data_type}\" object") from None
        self.parameters = []
        if parameters:
            for parameter in parameters.split(", "):
                parameter = parameter.split(" ")
                self.parameters.append(Variable(parameter[0][1:], parameter[1], "0"))

    def do_nothing(self, *args):
        return ",".join(args)