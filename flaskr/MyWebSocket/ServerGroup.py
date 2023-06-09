from typing import Dict, Any
from typing import TYPE_CHECKING

from flaskr.exception import ResultError

if TYPE_CHECKING:
    from websocket.server import WebsocketServer

from flaskr.MyWebSocket import Server


class ServerGroup:
    """
    Attributes:
        server_map : 保存 :class:`WebsocketServer` 的字典
    """
    server_map: dict[str, Any] = {}

    @classmethod
    def add(cls, server: Server):
        """
        添加websocketServer
        :param server: :class:`WebsocketServer`
        """
        cls.server_map[server.name] = server
        print(cls.server_map)

    @classmethod
    def remove(cls, server_name: str):
        """
        移除websocketServer
        :param server_name: websocketServer的名称
        """
        del cls.server_map[server_name]
        print(cls.server_map)

    @classmethod
    def get_front(cls) -> Any:
        """
        获取和前端进行通信的WebSocketServer.

        :return: 和前端进行通信的 :class:`WebsocketServer`.
        """
        ws = cls.server_map.get('front')
        if ws is None:
            raise ResultError(message='获取和前端进行通信的WebSocketServer失败')
        return ws
