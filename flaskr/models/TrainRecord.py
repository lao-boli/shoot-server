import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Double, false, ForeignKey
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from .base import Base, db
from flaskr.exception import ResultError


class TrainRecord(Base):
    __tablename__ = 'train_record'
    id = Column(String(255), primary_key=True, comment='训练记录id')
    train_time = Column(DateTime, comment='训练时间')
    shooter_id = Column(String(255), ForeignKey('shooter.id'), comment='射手id')

    shoot_data_r = db.relationship('ShootData', backref='TrainRecord', lazy='dynamic')
    shoot_data_list = []

    def serialize(self):
        s = super().serialize()
        s['shoot_data_list'] = self.serialize_list(self.order_list)
        del s['shoot_data_r']
        return s

    @classmethod
    def get_by_record_id(cls, record_id):
        record = super().get_by({id: record_id})
        record.shoot_data_list = record.shoot_data_r.all()
        return record

    @classmethod
    def list(cls, params):
        records = super().list(params)
        for record in records:
            record.shoot_data_list = record.shoot_data_r.all()
        return records

    @classmethod
    def update(cls, data: dict, key='dataId', err_msg='未找到射击数据'):
        super().update(data, key, err_msg)

    @classmethod
    def delete(cls, model_id, err_msg='未找到射击数据'):
        super().delete(model_id, err_msg)
