# 导入 Flask 和需要用到的模块
from functools import wraps
from flask import g

from flaskr import ResultError


def requires_roles(roles: list):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = g.user.role_id
            if user_role not in roles:
                raise ResultError(message='无权访问')
            return f(*args, **kwargs)

        return decorated_function

    return decorator
