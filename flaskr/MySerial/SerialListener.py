import asyncio

import serial
import serial_asyncio

from flaskr.MySerial.ShootHandler import ShootHandler
import logging

logger = logging.getLogger(__name__)


class SerialProtocol(asyncio.Protocol):

    def __init__(self):
        self.transport = None
        self.count = 0
        self.data_cache = None

    def reset_count(self):
        self.count = 0

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f'port opened: {transport}')

    def data_received(self, data):
        # 处理接收到的数据
        print(list(data))
        if self.data_cache is None:
            self.data_cache = list(data)
            self.count += 1
        else:
            self.data_cache.extend(data)
            self.count += 1
        # retry times : 3
        if len(self.data_cache) < 15 and self.count < 3:
            self.pause_reading()
        else:
            print('data_cache: ', self.data_cache)
            ShootHandler.on_recv(list(self.data_cache))
            self.reset_count()
            self.data_cache = None

    def write_data(self, data: bytes):
        print(list(data))
        self.transport.write(data)

    def connection_lost(self, exc):
        # 连接被关闭
        print('Serial port closed')

    def pause_writing(self):
        print('pause writing')

    def resume_writing(self):
        print('resume writing')

    def pause_reading(self):
        print('pause reading')
        # This will stop the callbacks to data_received
        self.transport.pause_reading()

    def resume_reading(self):
        # This will start the callbacks to data_received again with all data that has been received in the meantime.
        # print('resume reading')
        self.transport.resume_reading()


handle = SerialProtocol()


async def start_listen_serial():
    try:
        transport, protocol = await serial_asyncio.create_serial_connection(asyncio.get_event_loop(), lambda: handle,
                                                                            '/dev/mySerial', 9600)

        while True:
            # 每隔30ms读取分片数据
            await asyncio.sleep(0.03)
            protocol.resume_reading()
    except serial.SerialException as e:
        logger.error(f"Serial Exception occurred: {e}")


if __name__ == '__main__':
    asyncio.run(start_listen_serial())
    while 1:
        pass
