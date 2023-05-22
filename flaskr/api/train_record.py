from flask import (
    Blueprint, request, jsonify
)

from flaskr.api.auth import login_required
from flaskr.models import TrainRecord, base, Result
import logging

logger = logging.getLogger(__name__)

api = Blueprint('train_record', __name__, url_prefix='/api/train-record')
db = base.db


@api.route('/list', methods=['GET'])
@login_required
def list_train_records():
    train_records = TrainRecord.list(request.args)
    return jsonify(Result.success(data=TrainRecord.serialize_list(train_records)))


@api.route('/page', methods=['GET'])
@login_required
def page_train_records():
    page_info = TrainRecord.page_to_dict(request.args)
    return jsonify(Result.success(data=page_info))


@api.route('/get/<string:train_record_id>', methods=['GET'])
@login_required
def get_train_record(train_record_id):
    train_record = TrainRecord.get_by_id(train_record_id)
    if train_record is None:
        return jsonify(Result.fail(msg='train_record not found'))
    return jsonify(train_record.serialize())


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


@api.route('/delete/<int:train_record_id>', methods=['DELETE'])
@login_required
def delete_train_record(train_record_id):
    train_record = TrainRecord.delete(train_record_id)
    return jsonify(Result.success(msg='删除用户成功'))


# not id

@api.route('/get', methods=['GET'])
@login_required
def get_train_record_no_id():
    return jsonify(Result.fail(msg='必须携带id'))


@api.route('/delete', methods=['DELETE'])
@login_required
def delete_train_record_no_id():
    return jsonify(Result.fail(msg='必须携带id'))
