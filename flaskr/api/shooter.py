import sqlalchemy.exc
from flask import (
    Blueprint, request, jsonify
)
from werkzeug.security import generate_password_hash

from flaskr import ResultError
from flaskr.api.auth import login_required
from flaskr.decorator import requires_roles
from flaskr.models import User, Shooter, base, Result
import logging
from sqlalchemy.exc import *

from flaskr.utils import auth_params,auth_params_direct

logger = logging.getLogger(__name__)

api = Blueprint('shooter', __name__, url_prefix='/api/shooter')
db = base.db


@api.route('/list', methods=['GET'])
@login_required
def list_shooters():
    shooters = Shooter.list(auth_params(['shooter'], {'username': 'username'}))
    return jsonify(Result.success(data=Shooter.serialize_list(shooters)))


@api.route('/page', methods=['GET'])
@login_required
def page_shooters():
    page_info = Shooter.page_to_dict(auth_params(['shooter'], {'username': 'username'}))
    return jsonify(Result.success(data=page_info))


@api.route('/get/<string:shooter_id>', methods=['GET'])
@login_required
def get_shooter(shooter_id):
    shooter = Shooter.get_by_id(shooter_id)
    if shooter is None:
        return jsonify(Result.fail(msg='shooter not found'))
    return jsonify(shooter.serialize())


@api.route('/add', methods=['POST'])
@login_required
@requires_roles(['admin', 'trainer'])
def add_shooter():
    try:
        with db.session.begin_nested():
            copy = request.json.copy()
            copy['password'] = generate_password_hash(request.json['password'])
            # 强制设置射手用户角色
            copy['role_id'] = 'shooter'
            User.add_no_commit(copy, exclude=['id'])
            Shooter.add_no_commit(request.json)
        db.session.commit()
    except DatabaseError as e:
        db.session.rollback()
        logger.warning(f"{e}\n INPUT JSON {request.json}")
        if 'Duplicate entry' in str(e):
            raise ResultError(message='键冲突')
        elif 'foreign key' in str(e):
            raise ResultError(message='外键所指的记录不存在')
        elif 'cannot be null' in str(e):
            raise ResultError(message='非空字段为空')
        else:
            raise ResultError(message='Database Error')
    except KeyError as e:
        logger.warning(f"KeyError: {e}\n INPUT JSON {request.json}")
        raise ResultError(message='非法参数')
    except Exception as e:
        logger.error(f"{e}\n INPUT JSON {request.json}")
        raise ResultError(message='系统异常')

    return jsonify(Result.success(msg='添加射手成功'))


@login_required
@api.route('/update', methods=['POST'])
@requires_roles(['admin', 'trainer'])
def update_shooter():
    shooter = Shooter.update(request.json)
    return jsonify(Result.success(msg='更新射手成功'))


@api.route('/delete/<int:shooter_id>', methods=['DELETE'])
@login_required
@requires_roles(['admin', 'trainer'])
def delete_shooter(shooter_id):
    shooter = Shooter.delete(shooter_id)
    return jsonify(Result.success(msg='删除射手成功'))


# not id

@api.route('/get', methods=['GET'])
@login_required
def get_shooter_no_id():
    return jsonify(Result.fail(msg='必须携带id'))


@api.route('/delete', methods=['DELETE'])
@login_required
@requires_roles(['admin', 'trainer'])
def delete_shooter_no_id():
    return jsonify(Result.fail(msg='必须携带id'))
