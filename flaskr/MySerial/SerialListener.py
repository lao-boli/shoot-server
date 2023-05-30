import asyncio

import serial_asyncio

from flaskr.MySerial.ShootHandler import ShootHandler


class SerialProtocol(asyncio.Protocol):

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)

    def data_received(self, data):
        # 处理接收到的数据
        print(list(data))
        ShootHandler.on_recv(list(data))

    def write_data(self, data: bytes):
        self.transport.write(data)

    def connection_lost(self, exc):
        # 连接被关闭
        print('Serial port closed')

    def pause_writing(self):
        print('pause writing')

    def resume_writing(self):
        print('resume writing')


handle = SerialProtocol()


async def start_listen_serial():
    await serial_asyncio.create_serial_connection(asyncio.get_event_loop(),
                                                  lambda: handle, 'COM2', 9600)
