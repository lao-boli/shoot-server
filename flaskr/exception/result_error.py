class ResultError(Exception):
    def __init__(self, code=40000, message='error'):
        self.code = code
        self.message = message
        super().__init__(message)
