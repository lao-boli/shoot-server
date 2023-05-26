import json

import random

from flask import (
    Blueprint, request, jsonify
)

from flaskr.MySerial.listener import MyListener
from flaskr.MySerial.SerialListener import handle
from flaskr.api.auth import login_required
from flaskr.models import User, Shooter, base, Result
import logging

logger = logging.getLogger(__name__)

api = Blueprint('device', __name__, url_prefix='/api/device')
db = base.db

from flaskr.MyWebSocket.ServerGroup import ServerGroup

ws_server = ServerGroup.server_map


@api.route('/test-decode', methods=['GET'])
def test_decode():
    MyListener.decode([0x16, 0x10, 0x10, 0x01, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, 0x46, 0x55, 0x17, 0x00, 0x88])
    return jsonify(Result.success(data='succ'))

@api.route('/test-on-recv', methods=['GET'])
def test_on_recv():
    x = random.randint(0, 0x64)
    y = random.randint(0, 0x64)
    curve = random.randint(0, 0x01)
    # MyListener.on_recv([0x16, 0x10, 0x10, 0x01, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, 0x46, 0x55, 0x17, 0x00, 0x88])
    MyListener.on_recv([0x16, 0x10, 0x10, curve, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, x, 0x55, y, 0x00, 0x88])
    return jsonify(Result.success(data='succ'))


@api.route('/update-dev-state', methods=['GET'])
def update_dev_state():
    handle.write_data(data='a')
    return jsonify(Result.success())

@api.route('/online', methods=['GET'])
def online():
    dev_state = {'type': 'devState', 'gunOnline': True, 'targetOnline': True}
    ws_server.broadcast(json.dumps(dev_state))
    return jsonify(Result.success(data=dev_state))


@api.route('/offline', methods=['GET'])
def offline():
    ws_server.broadcast(json.dumps({'type': 'devState', 'gunOnline': False, 'targetOnline': False}))
    return jsonify(Result.success())

