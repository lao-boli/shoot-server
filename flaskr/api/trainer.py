from flask import (
    Blueprint, request, jsonify
)

from flaskr.api.auth import login_required
from flaskr.models import Trainer, base, Result
import logging

logger = logging.getLogger(__name__)

api = Blueprint('trainer', __name__, url_prefix='/api/trainer')
db = base.db


@api.route('/list', methods=['GET'])
@login_required
def list_trainers():
    trainers = Trainer.list(request.args)
    return jsonify(Result.success(data=Trainer.serialize_list(trainers)))


@api.route('/page', methods=['GET'])
@login_required
def page_trainers():
    page_info = Trainer.page_to_dict(request.args)
    return jsonify(Result.success(page_info))


@api.route('/get/<string:trainer_id>', methods=['GET'])
@login_required
def get_trainer(trainer_id):
    trainer = Trainer.get_by_id(trainer_id)
    if trainer is None:
        return jsonify(Result.fail(msg='trainer not found'))
    return jsonify(trainer.serialize())


@api.route('/add', methods=['POST'])
@login_required
def add_trainer():
    trainer = Trainer.add(request.json)
    return jsonify(Result.success(msg='添加用户成功'))


@login_required
@api.route('/update', methods=['POST'])
def update_trainer():
    trainer = Trainer.update(request.json)
    return jsonify(Result.success(msg='更新用户成功'))


@api.route('/delete/<int:trainer_id>', methods=['DELETE'])
@login_required
def delete_trainer(trainer_id):
    trainer = Trainer.delete(trainer_id)
    return jsonify(Result.success(msg='删除用户成功'))


# not id

@api.route('/get', methods=['GET'])
@login_required
def get_trainer_no_id():
    return jsonify(Result.fail(msg='必须携带id'))


@api.route('/delete', methods=['DELETE'])
@login_required
def delete_trainer_no_id():
    return jsonify(Result.fail(msg='必须携带id'))
