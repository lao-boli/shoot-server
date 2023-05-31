import json
import asyncio

import random

from flask import (
    Blueprint, request, jsonify
)

from flaskr.MySerial.ShootHandler import ShootHandler
from flaskr.MySerial.SerialListener import handle
from flaskr.api.auth import login_required
from flaskr.models import User, Shooter, base, Result
import logging
import flask_excel as excel

logger = logging.getLogger(__name__)

api = Blueprint('download', __name__, url_prefix='/api/download')
db = base.db

from flaskr.MyWebSocket.ServerGroup import ServerGroup

ws_server = ServerGroup.get_front()


@api.route('/excel/train-record', methods=['GET'])
def download_train_record_excel():
    ShootHandler.decode([0x16, 0x10, 0x10, 0x01, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, 0x46, 0x55, 0x17, 0x00, 0x88])
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")


@api.route('/test-on-recv', methods=['GET'])
def test_on_recv():
    x = random.randint(0, 0x64)
    y = random.randint(0, 0x64)
    curve = random.randint(0, 0x01)
    # MyListener.on_recv([0x16, 0x10, 0x10, 0x01, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, 0x46, 0x55, 0x17, 0x00, 0x88])
    ShootHandler.on_recv([0x16, 0x10, 0x10, curve, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, x, 0x55, y, 0x00, 0x88])
    return jsonify(Result.success(data='succ'))


@api.route('/config', methods=['POST'])
def config():
    conf = {
        "voiceTargetReporting": False,  # 语音报靶
        "toggleSwitch": False,  # 拉栓开关
        "recoilForceFeedback": False,  # 后坐力反馈
        "lowBatteryThreshold": 10,  # #低电量门限
        "speakerVolume": 1,  # 喇叭音量
        "cartridgeCapacity": 1  # 弹夹容量
    }
    # 下发配置数据
    conf = request.json
    config_command = [0x16, 0x11, 0x01, 0x00, 0x7b, 0x01, 0xc8, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    config_command[9] = conf["cartridgeCapacity"]
    config_command[10] = conf["voiceTargetReporting"]
    config_command[11] = conf["toggleSwitch"]
    config_command[12] = conf["recoilForceFeedback"]
    config_command[13] = conf["lowBatteryThreshold"]
    config_command[14] = conf["speakerVolume"]

    handle.write_data(data=bytes(config_command))

    return jsonify(Result.success())


@api.route('/online', methods=['GET'])
def online():
    dev_state = {'type': 'devState', 'gunOnline': True, 'targetOnline': True}
    asyncio.run(ws_server.broadcast(json.dumps(dev_state)))
    return jsonify(Result.success(data=dev_state))


@api.route('/offline', methods=['GET'])
def offline():
    asyncio.run(ws_server.broadcast(json.dumps({'type': 'devState', 'gunOnline': False, 'targetOnline': False})))
    return jsonify(Result.success())
