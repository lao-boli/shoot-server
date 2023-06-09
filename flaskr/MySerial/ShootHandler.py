import datetime
import json
import random
from flaskr import ShootData
import asyncio
from .constant import *
from flaskr.MyWebSocket.ServerGroup import ServerGroup
from flaskr.utils import StyleFormatter
from flaskr.utils.MyJsonEncoder import MyJSONEncoder


class ShootHandler:
    """
    射击业务处理器,桥接http,websocket,serial三方的数据交互
    Attributes:
        sequence: 弹序，默认为1，每次训练开始后重置为1
        train_record_id: 训练记录id，每次训练开始后需要进行设置
    """

    sequence = 1
    train_record_id = None

    @classmethod
    def on_recv(cls, data: list) -> None:
        """
        接收到串口消息后的业务处理函数


        :param data: bytes数组
        """

        from app import app
        app.app_context().push()
        # 数据长度小于15，直接丢弃
        if len(data) < 15:
            return
        coord, shoot_data = cls.decode(data)

        if shoot_data is not None and cls.train_record_id is not None:
            # 插入数据库
            shoot_data.record_id = cls.train_record_id
            ShootData.add_model(shoot_data)

        if coord is not None:
            # 串口测试与真机采用这种方式
            asyncio.get_event_loop().create_task(ServerGroup.get_front().broadcast(
                json.dumps(StyleFormatter.snake_to_camel_dict(coord), cls=MyJSONEncoder)))
            # http 测试采用这种方式
            # asyncio.run(ServerGroup.get_front().broadcast(
            #     json.dumps(StyleFormatter.snake_to_camel_dict(coord), cls=MyJSONEncoder)))

    @classmethod
    def start(cls, train_record_id):
        cls.reset()
        cls.train_record_id = train_record_id

    @classmethod
    def stop(cls):
        cls.reset()

    @classmethod
    def reset(cls):
        cls.sequence = 1
        cls.train_record_id = None

    @classmethod
    def decode(cls, raw: list):
        """
        解码硬件数据\n
        .. image:: file:///D:/IdeaProjects/shoot-server/flaskr/doc/data_info_frame.png
        <BLANKLINE>

        .. image:: file:///D:/IdeaProjects/shoot-server/flaskr/doc/register_info_frame.png

        e.g:\n
        轨迹坐标:
            [0x16, 0x10, 0x10, 0x01, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, 0x46, 0x55, 0x17, 0x00, 0x88]
        注册消息:
            [0x16, 0x20, 0x01, 0x01, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, 0x46, 0x55, 0x17, 0x00, 0x88]

        :param raw: 16进制数组
        :return: coord: :class:`dict` - 轨迹坐标 , shoot_data: :class:`ShootData` - 射击数据
        """
        # 第一位 不是0x16丢掉
        if CORE_WEB != raw[HEADER1]:
            return None, None
        # 第三位 用来判断上行下行信息的 后端发过去是01 收到的是10
        if UPLINK != raw[HEADER3]:
            return None, None

        # 第二位 0x10 为数据信息
        if DATA == raw[HEADER2]:
            coord = {}
            coord['axisX'] = int(raw[AXIS_X_HIGH]) + int(raw[AXIS_X_LOW]) / 100
            coord['axisY'] = int(raw[AXIS_Y_HIGH]) + int(raw[AXIS_Y_LOW]) / 100
            # 轨迹数据
            if CURVE == raw[DATA_TYPE]:
                coord['curve'] = True
            # 射击数据
            elif SHOOT_DATA == raw[DATA_TYPE]:
                coord['curve'] = False
                coord['sequence'] = cls.sequence

                # region generate shoot data
                shoot_data = ShootData()
                shoot_data.sequence = cls.sequence
                shoot_data.shoot_time = datetime.datetime.now()
                shoot_data.hit_ring_number = int(raw[HIT_RING_NUMBER]) / 10
                shoot_data.aim_ring_number = int(raw[AIM_RING_NUMBER]) / 10
                shoot_data.gun_shaking = int(raw[GUN_SHAKING])
                shoot_data.gun_shaking_rate = int(raw[GUN_SHAKING_RATE])
                shoot_data.fire_shaking = int(raw[FIRE_SHAKING])
                shoot_data.fire_shaking_rate = int(raw[FIRE_SHAKING_RATE])
                cls.score(shoot_data)
                # endregion

                coord.update(shoot_data.serialize())
                cls.sequence += 1
                print(shoot_data.serialize())
                return coord, shoot_data

            print(coord)
            return coord, None

        # TODO: maybe cause bug, determine HEADER2 first in future
        # 第九位 ack 只有第二位00有效
        if ENROLL_REQUEST == raw[ACK]:
            raw[ACK] = CONFIRM_ENROLL
            raw[HEADER3] = DOWNLINK
            # 向串口下发收到注册消息
            from flaskr.MySerial.SerialListener import handle
            handle.write_data(bytes(raw))
        return None, None

    @classmethod
    def score(cls, shoot_data: ShootData):
        hit_ring_number = cls.ring_number(shoot_data.hit_ring_number, 6, 8, 9, 10)
        aim_ring_number = cls.ring_number(shoot_data.aim_ring_number, 6, 8, 9, 10)
        gun_shaking = cls.score_number(shoot_data.gun_shaking, 60, 50, 31, 0)
        gun_shaking_rate = cls.score_number(shoot_data.gun_shaking_rate, 24, 19, 13, 0)
        fire_shaking = cls.score_number(shoot_data.fire_shaking, 45, 30, 15, 0)
        fire_shaking_rate = cls.score_number(shoot_data.fire_shaking_rate, 15, 10, 5, 0)

        shooting_accuracy = hit_ring_number * 0.529 + aim_ring_number * 0.471
        gun_stability = gun_shaking * 0.512 + gun_shaking_rate * 0.488
        firing_stability = fire_shaking * 0.513 + fire_shaking_rate * 0.497

        score = shooting_accuracy * 0.344 + gun_stability * 0.34 + firing_stability * 0.316

        shoot_data.shooting_accuracy = round(shooting_accuracy, 2)
        shoot_data.gun_stability = round(gun_stability, 2)
        shoot_data.fire_stability = round(firing_stability, 2)
        shoot_data.score = round(score, 2)

    @classmethod
    def score_number(cls, data: float, passed: float, middle: float, good: float, excellent: float):
        """
        计算射击的分数,射击数据原始值比分数线值越小越优秀

        :param data:     射击成绩原始值
        :param passed:    及格分数值
        :param middle:    中等分数值
        :param good:      良好分数值
        :param excellent: 优秀分数值
        :return: 射击分数
        """
        if data > passed:
            return 25.0
        elif passed >= data > middle:
            return (data - passed) / (middle - passed) * 50 + 25
        elif middle >= data > good:
            return (data - middle) / (good - middle) * 25 + 75
        return (data - good) / (excellent - good) * 10 + 90

    @classmethod
    def ring_number(cls, ring: float, passed: float, middle: float, good: float, excellent: float):
        """
        计算射击的环值分数,环值比分数线值越大越优秀

        :param ring: 环值
        :param passed:    及格分数值
        :param middle:    中等分数值
        :param good:      良好分数值
        :param excellent: 优秀分数值
        :return: 环值分数
        """
        if ring < passed:
            return (ring / passed) * 25.0
        elif passed <= ring < middle:
            return (ring - passed) / (middle - passed) * 51 + 25
        elif middle <= ring < good:
            return (ring - middle) / (good - middle) * 25 + 75
        return (ring - good) / (excellent - good) * 10 + 90


if __name__ == '__main__':
    r = random.randint(0, 0x64)
    print(r)
    v = round(100.45699999999, 3)
    print(v)
    arr = [0x16, 0x10, 0x10, 0x01, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, 0x46, 0x55, 0x17, 0x00, 0x88]
    print(arr)
    print(bytes(arr))
    ShootHandler.decode(arr)

'16 10 10 01 56 24 15 56 14 18 46 55 17 00 88'
'16 10 10 01 56 24 15 56 14 18 46 55 17 00 88'
