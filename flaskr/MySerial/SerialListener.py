import asyncio

import serial
import serial_asyncio


async def listen_serial(port, baudrate):
    # 创建一个 Serial 对象
    # ser = serial.Serial(port=port, baudrate=baudrate)
    # 将 Serial 对象包装为一个流式传输对象
    transport, protocol = await serial_asyncio.create_serial_connection(asyncio.get_event_loop(),
                                                                        lambda: SerialProtocol(), port, baudrate)
    # 等待连接完成
    await asyncio.sleep(0.5)
    return transport, protocol


class SerialProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)

    def data_received(self, data):
        # 处理接收到的数据
        print(data.decode('utf8'))

    def connection_lost(self, exc):
        # 连接被关闭
        print('Serial port closed')


async def main():
    transport, protocol = await listen_serial('COM3', 9600)
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        transport.close()


if __name__ == '__main__':
    asyncio.run(main())
