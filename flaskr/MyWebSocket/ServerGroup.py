from flaskr import WebSocketServer


class ServerGroup:
    server: WebSocketServer = None

    @classmethod
    def add(cls, server):
        cls.server = server
        print(cls.server)
