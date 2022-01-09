class EmptyClipboard(BaseException):
    def __init__(self, source: str, err_index: int, message: str="Cannot paste from empty clipboard"):
        self.message = message
        self.source = source
        self.index = err_index
        super().__init__(self.message)


class UnexpectedCharacter(BaseException):
    def __init__(self, source: str, err_index: int, message=None):
        self.message = message
        self.source = source
        self.index = err_index
        if not message:
            self.message = f"Unexpected character \"{self.source[err_index-1]}\""
        super().__init__(self.message)


class InvalidDataType(BaseException):
    def __init__(self, invalid_data_type):
        self.message = f"\"{invalid_data_type}\" is not a valid data type"
        super().__init__(self.message)

class SegmentationFault(BaseException):
    def __init__(self, message):
        super().__init__(message)

class EndOfProgramError(BaseException):
    def __init__(self, message):
        super().__init__(message)