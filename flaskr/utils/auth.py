from flask import request, g

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flaskr.models.user import User


def auth_params(exclude: list = None, params: dict = None):
    """
    为查询请求强制添加查询参数

    :param exclude: 要排除的角色列表
    :param params: 要强制添加的参数字典. key - 查询参数名称, value - :class:`User` 的属性名
    :return: 强制添加参数后的字典
    """
    if exclude is None:
        exclude = []
    if params is None:
        params = {}
    # 在排除角色内,直接返回原参数
    if g.user.role_id in exclude:
        return request.args

    after_auth = request.args.copy()
    for k, v in params.items():
        after_auth[k] = g.user.__getattribute__(v)
    return after_auth
