import asyncio

import serial
import serial_asyncio

from flaskr.MySerial.listener import MyListener


class SerialProtocol(asyncio.Protocol):

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)

    def data_received(self, data):
        # 处理接收到的数据
        print(list(data))
        MyListener.on_recv(list(data))

    def write_data(self, data):
        self.transport.write(b'Hello, World!\n')

    def connection_lost(self, exc):
        # 连接被关闭
        print('Serial port closed')

    def pause_writing(self):
        print('pause writing')

    def resume_writing(self):
        print('resume writing')


handle = SerialProtocol()


async def listen_serial(port, baudrate):
    coro = await serial_asyncio.create_serial_connection(asyncio.get_event_loop(),
                                                         lambda: SerialProtocol(), port, baudrate)
    return coro


async def start_listen_serial():
    await serial_asyncio.create_serial_connection(asyncio.get_event_loop(),
                                                  lambda: handle, 'COM2', 9600)


def run():
    try:
        asyncio.run(start_listen_serial())
        # print(transport)
    except KeyboardInterrupt:
        pass


def run2():
    loop = asyncio.get_event_loop()
    coro = listen_serial('COM3', 9600)
    transport, protocol = loop.run_until_complete(coro)
    print(transport)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == '__main__':
    run()
