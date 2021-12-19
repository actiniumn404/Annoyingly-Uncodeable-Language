import string
from errors import *

class Compile:
    def __init__(self, code):
        self.source = code
        self.curPos = 0
        self.curChar = ""
        self.location = None
        self.clipboard = None
        self.valid = list(string.whitespace)+list(string.ascii_lowercase)+["\0", "", "\n", "!", "c", "v", "m", "p", "#", "*", "+", "/", "-"]
        self.memory = ""
        self.memory_state = "end"
        self.out = print
        self.variables = {}

        self.parse()

    def next_char(self):
        if self.curPos >= len(self.source):
            # End of Line
            self.curChar = "\0"
            return
        self.curChar = self.source[self.curPos]
        self.curPos += 1

    def peek(self):
        if self.curPos+1 >= len(self.source):
            # End of Line
            return "\0"
        return self.source[self.curPos+1]

    def parse(self):
        while self.curChar != "\0":
            # take care of copy paste
            if self.curChar == "#":
                while self.curChar != "\n" and self.curChar != "\0":
                    self.next_char()
            # "INput"
            if self.curChar == "i":
                self.next_char()
                if self.curChar == "n":
                    if self.memory_state == "start":
                        user_input = input()
                        if user_input.isnumeric():
                            user_input = int(user_input)
                        self.memory += user_input
            # Memory Clear
            if self.curChar == "m":
                self.next_char()
                if self.curChar == "c":
                    self.memory = ""

            # Variables
            if self.curChar == "$":
                self.next_char()
                name = ""
                while self.curChar not in [" ", "\n", "\0"]:
                    name += self.curChar
                    self.next_char()
                self.variables[name] = self.memory

            # "Commands"
            if self.curChar == "!":
                self.next_char()
                # Copy
                if self.curChar == "c":
                    self.clipboard = self.memory

                # Paste
                elif self.curChar == "v":
                    if not self.clipboard:
                        raise EmptyClipboard(self.source, self.curPos)
                    else:
                        self.memory = self.clipboard

                # Print
                elif self.curChar == "p":
                    if self.memory and self.memory_state == "end":
                        self.out(self.memory)

                # Mathematical Computations
                elif self.source[self.curPos-1:self.curPos+3] == "math":
                    for _ in range(5):
                        self.next_char()
                    operand1 = ""
                    operand2 = ""
                    while self.curChar in ["c", "v"]:
                        operand1 += {"c": "0", "v": "1"}.get(self.curChar)
                        self.next_char()
                    operation = self.curChar
                    self.next_char()
                    while self.curChar in ["c", "v"]:
                        operand2 += {"c": "0", "v": "1"}.get(self.curChar)
                        self.next_char()
                    operand1 = int(operand1, 2)
                    operand2 = int(operand2, 2)
                    if operation == "+":
                        result = operand1+operand2
                    if operation == "-":
                        result = operand1-operand2
                    if operation == "*":
                        result = operand1*operand2
                    if operation == "/":
                        result = operand1/operand2
                    if self.memory_state == "start":
                        self.memory += str(result)


                # Memory (start/end)
                elif self.curChar == "m":
                    before = self.memory_state
                    if before == "end":
                        self.memory_state = "start"
                        #self.memory = ""
                    else:
                        self.memory_state = "end"
                self.next_char()


            elif self.curChar in ["c", "v"]:
                binary = ""
                while self.curChar in ["c", "v"]:
                    binary += {"c": "0", "v": "1"}.get(self.curChar)
                    self.next_char()
                if self.memory_state == "start":
                    self.memory += chr(int(binary, 2))

            elif self.curChar == ">":
                self.next_char()
                self.next_char()
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
                    self.next_char()
                self.out = open(file_name, "w").write

            elif self.curChar in self.valid:
                self.next_char()
            else:
                raise UnexpectedCharacter(self.source, self.curPos)
