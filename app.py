from flask_migrate import Migrate

from flaskr import create_app
from flaskr.models.base import db

# import logging
# logger = logging.getLogger(__name__)
#
app = create_app()
migrate = Migrate(app=app, db=db)


if __name__ == '__main__':
    pass
    # app.run()


    # use idea 在运行配置中开启debug和设置端口
    # app.run()
