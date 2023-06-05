from flask import (
    Blueprint, request, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr.api.auth import login_required
from flaskr.decorator import requires_roles
from flaskr.models import User, base, Result
import logging

logger = logging.getLogger(__name__)

api = Blueprint('user', __name__, url_prefix='/api/user')
db = base.db


@api.route('/list', methods=['GET'])
@login_required
def list_users():
    users = User.list(request.args)
    return jsonify(Result.success(data=User.serialize_list(users)))


@api.route('/page', methods=['GET'])
@login_required
def page_users():
    page_info = User.page_to_dict(request.args)
    return jsonify(Result.success(page_info))


@api.route('/get/<int:user_id>', methods=['GET'])
@login_required
@requires_roles(['admin'])
def get_user(user_id):
    user = User.get_by_id(user_id)
    if user is None:
        return jsonify(Result.fail(msg='user not found'))
    return jsonify(user.serialize())


@api.route('/add', methods=['POST'])
@login_required
def add_user():
    user = User.add(request.json)
    return jsonify(Result.success(msg='添加用户成功'))


@login_required
@api.route('/update', methods=['POST'])
def update_user():
    user = User.update(request.json)
    return jsonify(Result.success(msg='更新用户成功'))


@login_required
@api.route('/change-password', methods=['POST'])
def change_password():
    copy = request.json.copy()
    if copy['oldPassword'] == copy['newPassword']:
        return jsonify(Result.fail(msg='两次输入密码相同'))

    user = User.get_by_id(copy['userId'])
    if user is None:
        return jsonify(Result.fail(msg='用户不存在'))
    if not check_password_hash(user.password, copy['oldPassword']):
        return jsonify(Result.fail(msg='原密码错误'))

    copy['password'] = generate_password_hash(request.json['newPassword'])
    user = User.update(copy)
    return jsonify(Result.success(msg='修改密码成功'))


@api.route('/delete/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.delete(user_id)
    return jsonify(Result.success(msg='删除用户成功'))


# not id

@api.route('/get', methods=['GET'])
@login_required
def get_user_no_id():
    return jsonify(Result.fail(msg='必须携带id'))


@api.route('/delete', methods=['DELETE'])
@login_required
def delete_user_no_id():
    return jsonify(Result.fail(msg='必须携带id'))
