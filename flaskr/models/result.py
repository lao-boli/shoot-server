from flaskr.exception import ResultError


class Result:
    def __init__(self, code: int, msg: str, data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def to_dict(self):
        return {"code": self.code, "msg": self.msg, "data": self.data}

    @classmethod
    def success(cls, code: int = 200, msg: str = 'success', data=None):
        return Result(code, msg, data).to_dict()

    @classmethod
    def fail(cls, code: int = 400, msg: str = 'fail', data=None):
        return Result(code, msg, data).to_dict()

    @classmethod
    def fail_with_error(cls, e: ResultError):
        return Result(e.code, e.message, None).to_dict()
