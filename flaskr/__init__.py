import asyncio

from flask import Flask, jsonify

from .MyWebSocket.Server import WebSocketServer
from .models import *
from .exception import ResultError
from .utils import MyJSONEncoder, ColoredLevelFormatter

from flask import Flask, jsonify
from flask_cors import CORS


import logging

logger = logging.getLogger(__name__)

server2 = WebSocketServer(9001)


async def main():
    await asyncio.gather(
        server2.start_server(),
    )


def run_ws():
    asyncio.run(main())


from threading import Thread


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app, resources=r'/*')

    setup_logging(app)

    ws = Thread(target=run_ws)
    ws.start()

    app.json_encoder = MyJSONEncoder
    app.debug = True
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:root@127.0.0.1:3306/pytest?charset=utf8',
        SQLALCHEMY_POOL_RECYCLE=1800,
        SQLALCHEMY_POOL_TIMEOUT=1500,
        SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
        SQLALCHEMY_ECHO=True,
    )

    # error handlers
    @app.errorhandler(Exception)
    def handle_runtime_error(e):
        app.logger.error('{}'.format(e))
        return jsonify(Result.fail(msg='未知异常'))

    @app.errorhandler(ResultError)
    def handle_result_error(e: ResultError):
        return jsonify(Result.fail_with_error(e))

    # db
    from .models.base import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # router
    from .api.user import api
    app.register_blueprint(api)

    from .api.order import api as order_api
    app.register_blueprint(order_api)

    from .api.auth import bp
    app.register_blueprint(bp)
    return app


def setup_logging(app):
    app.logger.setLevel(logging.DEBUG)
    formatter = ColoredLevelFormatter(
        "\033[38;2;187;187;187m%(asctime)s\033[0m "
        "%(levelname)s "
        "\033[36m%(name)s\033[0m"
        "\033[38;2;187;187;187m: %(message)s\033[0m"
    )
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)
