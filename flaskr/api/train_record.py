import json
from datetime import datetime

from flask import (
    Blueprint, request, jsonify, g, make_response
)

from flaskr.MySerial.ShootHandler import ShootHandler
from flaskr.api.auth import login_required
from flaskr.decorator import requires_roles
from flaskr.models import TrainRecord, base, Result
import logging

from flaskr.utils import auth_params, auth_params_direct

logger = logging.getLogger(__name__)

api = Blueprint('train_record', __name__, url_prefix='/api/train-record')
db = base.db


@api.route('/list', methods=['GET'])
@login_required
def list_train_records():
    train_records = TrainRecord.list(auth_params(['shooter'], {'username': 'username'}))
    return jsonify(Result.success(data=TrainRecord.serialize_list(train_records)))


@api.route('/page', methods=['GET'])
@login_required
def page_train_records():
    page_info = TrainRecord.page_to_dict(
        auth_params_direct(['shooter'], {'shooterId': g.user.shooter_r.id if g.user.shooter_r else None}))
    return jsonify(Result.success(data=page_info))


@api.route('/get/<string:train_record_id>', methods=['GET'])
@login_required
def get_train_record(train_record_id):
    train_record = TrainRecord.get_by_id(train_record_id)
    if train_record is None:
        return jsonify(Result.fail(msg='train_record not found'))
    return jsonify(train_record.serialize())


@api.route('/start', methods=['POST'])
@login_required
def start_train():
    shooter_id = request.json['shooterId']
    train_record = TrainRecord.add({'shooter_id': shooter_id, 'train_time': datetime.now()})
    ShootHandler.start(train_record_id=train_record.id)
    # XXX 直接返回空字符串或许会更好处理一些,但是写都写了,就这样吧
    resp = make_response(jsonify(Result.success(msg='开始训练', data=train_record.serialize())))
    resp.headers['hide-msg'] = True
    return resp


@api.route('/stop', methods=['POST'])
@login_required
def stop_train():
    ShootHandler.stop()
    resp = make_response(jsonify(Result.success(msg='结束训练')))
    resp.headers['hide-msg'] = True
    return resp


@api.route('/add', methods=['POST'])
@login_required
def add_train_record():
    train_record = TrainRecord.add(request.json)
    return jsonify(Result.success(msg='添加用户成功'))


@login_required
@api.route('/update', methods=['POST'])
def update_train_record():
    train_record = TrainRecord.update(request.json)
    return jsonify(Result.success(msg='更新用户成功'))


@api.route('/delete/<string:train_record_id>', methods=['DELETE'])
@login_required
@requires_roles(['admin', 'trainer'])
def delete_train_record(train_record_id):
    train_record = TrainRecord.delete(train_record_id)
    return jsonify(Result.success(msg='删除训练记录成功'))


# not id

@api.route('/get', methods=['GET'])
@login_required
def get_train_record_no_id():
    return jsonify(Result.fail(msg='必须携带id'))


@api.route('/delete', methods=['DELETE'])
@login_required
@requires_roles(['admin', 'trainer'])
def delete_train_record_no_id():
    return jsonify(Result.fail(msg='必须携带id'))
