class EmptyClipboard(BaseException):
    def __init__(self, source: str, err_index: int, message: str="Cannot paste from empty clipboard"):
        self.message = message
        self.source = source
        self.index = err_index
        super().__init__(self.message)

    def __str__(self):
        context = self.source[max(0, self.index - 10):min(len(self.source), self.index + 10)]
        arrows = "-"*(len(f"(Error at character {self.index}: ") + (self.index-max(0, self.index - 10))-1)+"^"
        return f"{self.message}\n(Error at character {self.index}: {context})\n{arrows}"


class UnexpectedCharacter(BaseException):
    def __init__(self, source: str, err_index: int, message=None):
        self.message = message
        self.source = source
        self.index = err_index
        if not message:
            message = f"Unexpected character \"{self.source[err_index-1]}\""
        super().__init__(self.message)

    def __str__(self):
        context = self.source[max(0, self.index - 10):min(len(self.source), self.index + 10)]
        arrows = "-"*(len(f"(Error at character {self.index}: ") + (self.index-max(0, self.index - 10))-1)+"^"
        return f"{self.message}\n(Error at character {self.index}: {context})\n{arrows}"
