import asyncio
import logging
import traceback

from flasgger import Swagger
from flask import Flask, jsonify
from flask_cors import CORS

from .MyWebSocket.Server import WebSocketServer
from .exception import ResultError
from .models import *
# start_listen_serial 必须在 导入models后才能导入
from flaskr.MySerial.SerialListener import start_listen_serial
from .utils import MyJSONEncoder, ColoredLevelFormatter
import flask_excel as excel

logger = logging.getLogger(__name__)

server = WebSocketServer(port=9001, name='front')


async def main():
    await asyncio.gather(
        server.start_server(),
        start_listen_serial()
    )


def run_ws():
    asyncio.run(main())


from threading import Thread


def get_ws():
    return server


def create_app(test_config=None):
    app = Flask(__name__)

    excel.init_excel(app)

    Swagger(app=app, template_file='doc/final.yml')

    CORS(app, resources={r'/*': {'supports_credentials': True, 'expose_headers': "Content-Disposition"}})

    setup_logging(app)

    ws = Thread(target=run_ws, daemon=True)
    ws.start()

    app.json_encoder = MyJSONEncoder

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:root@127.0.0.1:3306/shoot?charset=utf8',
        SQLALCHEMY_POOL_RECYCLE=1800,
        SQLALCHEMY_POOL_TIMEOUT=1500,
        SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
        SQLALCHEMY_ECHO=True,
    )

    # error handlers

    @app.errorhandler(404)
    def handle_error(e):
        response = jsonify({'error': 'Not found'})
        response.status_code = 404
        return response

    @app.errorhandler(405)
    def handle_error(e):
        response = jsonify({'error': '405'})
        response.status_code = 405
        return response

    @app.errorhandler(Exception)
    def handle_runtime_error(e):
        app.logger.error('{}'.format(e))
        traceback.print_exc()
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

    from .api.shooter import api
    app.register_blueprint(api)

    from .api.trainer import api
    app.register_blueprint(api)

    from .api.train_record import api
    app.register_blueprint(api)

    from .api.device import api
    app.register_blueprint(api)

    from .api.auth import bp
    app.register_blueprint(bp)

    from .api.download import api
    app.register_blueprint(api)

    return app


def setup_logging(app):
    app.logger.setLevel(logging.DEBUG)
    # console logger
    formatter = ColoredLevelFormatter(
        "\033[38;2;187;187;187m%(asctime)s\033[0m "
        "%(levelname)s "
        "\033[36m%(name)s\033[0m"
        "\033[38;2;187;187;187m: %(message)s\033[0m"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt=formatter)

    # file logger
    file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    log_folder = 'log'
    import os
    os.makedirs(f'{log_folder}/info', exist_ok=True)
    os.makedirs(f'{log_folder}/error', exist_ok=True)
    from logging.handlers import TimedRotatingFileHandler
    file_info_handler = TimedRotatingFileHandler(filename='./log/info/shoot.log', encoding='utf-8', interval=1,
                                                 when='midnight', backupCount=7)
    file_info_handler.setLevel('INFO')
    file_info_handler.setFormatter(fmt=file_formatter)
    file_info_handler.flushTime = 5.0

    file_error_handler = TimedRotatingFileHandler(filename='./log/error/shoot.log', encoding='utf-8', interval=1,
                                                  when='midnight', backupCount=7)
    file_error_handler.setLevel('ERROR')

    file_error_handler.setFormatter(fmt=file_formatter)
    file_error_handler.flushTime = 5.0

    app.logger.handlers.clear()
    app.logger.addHandler(file_info_handler)
    app.logger.addHandler(file_error_handler)
    app.logger.addHandler(console_handler)

    # 接管sqlalchemy的log
    logging.getLogger('sqlalchemy.engine.Engine').handlers.clear()
    logging.getLogger('sqlalchemy.engine.Engine').addHandler(console_handler)
    logging.getLogger('sqlalchemy.engine.Engine').addHandler(file_info_handler)
    logging.getLogger('sqlalchemy.engine.Engine').addHandler(file_error_handler)
