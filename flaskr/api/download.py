import logging

import flask_excel as excel
from flask import (
    Blueprint
)

from flaskr import TrainRecord
from flaskr.models import base

logger = logging.getLogger(__name__)

api = Blueprint('download', __name__, url_prefix='/api/download')
db = base.db


@api.route('/excel/train-record', methods=['GET'])
def download_train_record_excel():
    records = TrainRecord.list({})
    res = map(lambda r: {"记录编号": r.id,
                         "射手编号": r.shooter.id if r.shooter else '',
                         "射手姓名": r.shooter.user.name if r.shooter else '',
                         "训练时间": r.train_time.strftime("%Y-%m-%d %H:%M:%S"),
                         "得分": str(list(map(lambda s: s.score, r.shoot_data_list)))},
              records)
    data = list(res)
    return excel.make_response_from_records(data, "xlsx", file_name="训练记录")
