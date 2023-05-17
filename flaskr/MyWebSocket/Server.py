import asyncio
from threading import Thread

import websockets
from websockets.legacy.server import WebSocketServerProtocol
import logging

logger = logging.getLogger(__name__)


class WebSocketServer:
    def __init__(self, port, on_close: callable = None, on_open: callable = None, on_message: callable = None):
        self.port = port
        self.server = None
        self.on_open = on_open
        self.on_close = on_close
        self.on_message = on_message
        self.connections = {}

    async def start_server(self):
        try:
            self.server = await websockets.serve(self.handler, "", self.port)
        except OSError as e:
            if e.args[0] == 10048:
                logger.warning('port already in bind')
            else:
                logger.error(e)
        logger.info(f"WebSocket server started on port {self.port}")
        await asyncio.Future()

    async def stop_server(self):
        if self.server:
            for websocket in self.connections.values():
                await websocket.close()

            self.connections = {}
            self.server.close()
            await self.server.wait_closed()

    @staticmethod
    def convert_addr(addr: tuple):
        """
        将addr tuple 转换成字符串.\n
        e.g: ((127.0.0.1),(8888)) -> "127.0.0.1:8888"
        :param addr: websocket address
        :return: str addr
        """
        return str(addr[0]) + ':' + str(addr[1])

    async def handler(self, websocket: WebSocketServerProtocol, path):
        # 获取当前连接的端口号
        client_addr = self.convert_addr(websocket.remote_address)
        # 将当前连接存储到 connections 字典中
        self.connections[client_addr] = websocket
        logger.info(f"server: {self.port} connected with client: {client_addr}")

        if self.on_open is not None:
            self.on_open(websocket)

        try:
            async for message in websocket:
                # 处理收到的消息
                logger.info(f"server: {self.port} Received message from {client_addr}: {message}")

                if self.on_message is not None:
                    self.on_message(websocket)

                # default echo
                await websocket.send(message)

        finally:
            # 当连接关闭时，从 connections 中移除该连接
            if self.convert_addr(websocket.remote_address) in self.connections.keys():

                if self.on_close is not None:
                    self.on_close(websocket)

                del self.connections[client_addr]
                logger.info(f"server: {self.port} client disconnected : {client_addr}\n"
                            f"current conns count: {self.connections.keys().__len__()}")

    async def broadcast(self, message):
        if self.server and self.connections.get(self.port):
            # 向指定端口的所有连接发送消息
            for conn in self.connections[self.port]:
                await conn.send(message)


async def main():
    server1 = WebSocketServer(8000, on_message=(lambda _: print('onmessage')))
    server2 = WebSocketServer(9001)
    await asyncio.gather(
        server1.start_server(),
        server2.start_server(),
    )


def run_ws():
    asyncio.run(main())


if __name__ == "__main__":
    loop = asyncio.run(main())