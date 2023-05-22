class ServerGroup:
    server = None

    @classmethod
    def add(cls, server):
        cls.server = server
        print(cls.server)
