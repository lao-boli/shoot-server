from flask import (
    Blueprint, request, jsonify
)

from flaskr.api.auth import login_required
from flaskr.models import Order, base, Result

api = Blueprint('order', __name__, url_prefix='/order')
db = base.db


@api.route('/list', methods=['GET'])
@login_required
def list_orders():
    orders = Order.list(request.args)
    return jsonify(Result.success(data=Order.serialize_list(orders)))


@api.route('/page', methods=['GET'])
@login_required
def page_orders():
    page_info = Order.page_to_dict(request.args)
    return jsonify(Result.success(page_info))


@api.route('/get/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = Order.get_by_id(order_id)
    if order is None:
        return jsonify(Result.fail(msg='order not found'))
    return jsonify(order.serialize())


@api.route('/add', methods=['POST'])
@login_required
def create_order():
    order = Order.add(request.json)
    return jsonify(Result.success(msg='添加订单成功'))


@login_required
@api.route('/update', methods=['POST'])
def update_order():
    order = Order.update(request.json)
    return jsonify(Result.success(msg='更新订单成功'))


@api.route('/delete/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    order = Order.delete(order_id)
    return jsonify(Result.success(msg='删除订单成功'))


# not id

@api.route('/get', methods=['GET'])
@login_required
def get_order_no_id():
    return jsonify(Result.fail(msg='必须携带id'))


@api.route('/delete', methods=['GET'])
@login_required
def delete_order_no_id():
    return jsonify(Result.fail(msg='必须携带id'))
