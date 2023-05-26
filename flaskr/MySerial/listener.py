import datetime
import json
import random

from flaskr import ShootData
import asyncio

from flaskr.MyWebSocket.ServerGroup import ServerGroup
from flaskr.utils import StyleFormatter
from flaskr.utils.MyJsonEncoder import MyJSONEncoder


class MyListener():
    sequence = 1
    train_record_id = None

    @classmethod
    def on_recv(cls, data):
        coord, shoot_data = cls.decode(data)

        if shoot_data is not None and cls.train_record_id is not None:
            # 插入数据库
            shoot_data.record_id = cls.train_record_id
            ShootData.add_self(shoot_data)

        # 串口测试与真机采用这种方式
        asyncio.get_event_loop().create_task(ServerGroup.get_front().broadcast(json.dumps(StyleFormatter.snake_to_camel_dict(coord), cls=MyJSONEncoder)))
        # http 测试采用这种方式
        # asyncio.run(
        #     ServerGroup.get_front().broadcast(json.dumps(StyleFormatter.snake_to_camel_dict(coord), cls=MyJSONEncoder)))

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
    def decode(cls, raw: list) -> (dict, ShootData):
        """
        解码硬件数据

        :param raw: 16进制数组
        :return: coord - 轨迹坐标 , shoot_data - 射击数据
        """
        # 第一位 不是0x16丢掉
        if 0x16 != raw[0]:
            return None, None
        # 第三位 用来判断上行下行信息的 后端发过去是01 收到的是10
        if 0x10 != raw[2]:
            return None, None

        # 第二位 10 为坐标信息
        if 0x10 == raw[1]:
            coord = {}
            coord['axisX'] = int(raw[10]) + int(raw[11]) / 100
            coord['axisY'] = int(raw[12]) + int(raw[13]) / 100
            # 轨迹数据
            if 0x00 == raw[3]:
                coord['curve'] = True
            # 射击数据
            elif 0x01 == raw[3]:
                coord['curve'] = False
                coord['sequence'] = cls.sequence

                # region generate shoot data
                shoot_data = ShootData()
                shoot_data.sequence = cls.sequence
                shoot_data.shoot_time = datetime.datetime.now()
                shoot_data.hit_ring_number = int(raw[4]) / 10
                shoot_data.aim_ring_number = int(raw[5]) / 10
                shoot_data.gun_shaking = int(raw[6])
                shoot_data.gun_shaking_rate = int(raw[7])
                shoot_data.fire_shaking = int(raw[8])
                shoot_data.fire_shaking_rate = int(raw[7])
                cls.score(shoot_data)
                # endregion

                coord.update(shoot_data.serialize())
                cls.sequence += 1
                print(shoot_data.serialize())
                return coord, shoot_data

            print(coord)
            return coord, None

        # 第九位 ack 只有第二位00有效
        if 0x00 == raw[8]:
            raw[8] = 0x99
            raw[2] = 0x01
            # TODO send to port
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
    def score_number(cls, a: float, b: float, c: float, d: float, e: float):
        if a > b:
            return 25.0
        elif b >= a > c:
            return (a - b) / (c - b) * 50 + 25
        elif c >= a > d:
            return (a - c) / (d - c) * 25 + 75
        return (a - d) / (e - d) * 10 + 90

    @classmethod
    def ring_number(cls, a: float, b: float, c: float, d: float, e: float):
        if a < b:
            return (a / b) * 25.0
        elif b <= a < c:
            return (a - b) / (c - b) * 51 + 25
        elif c <= a < d:
            return (a - c) / (d - c) * 25 + 75
        return (a - d) / (e - d) * 10 + 90


if __name__ == '__main__':
    r = random.randint(0, 0x64)
    print(r)
    v = round(100.45699999999, 3)
    print(v)
    arr = [0x16, 0x10, 0x10, 0x01, 0x56, 0x24, 0x15, 0x56, 0x14, 0x18, 0x46, 0x55, 0x17, 0x00, 0x88]
    print(arr)
    MyListener.decode(arr)

'16 10 10 01 56 24 15 56 14 18 46 55 17 00 88'
