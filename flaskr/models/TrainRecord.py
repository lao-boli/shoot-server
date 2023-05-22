from sqlalchemy import Column, String, DateTime, ForeignKey

from flaskr.models.Shooter import Shooter
from .base import Base, db
from .user import User


class TrainRecord(Base):
    __tablename__ = 'train_record'
    id = Column(String(255), primary_key=True, comment='训练记录id')
    train_time = Column(DateTime, comment='训练时间')
    shooter_id = Column(String(255), ForeignKey('shooter.id'), comment='射手id')

    shoot_data_r = db.relationship('ShootData', backref='TrainRecord', lazy='dynamic')
    shoot_data_list = []

    def serialize(self, to_camel=True):
        s = super().serialize()
        s['shoot_data_list'] = self.serialize_list(self.shoot_data_list)
        if s['shooter'] is not None:
            shooter: Shooter = s['shooter']
            s['shooter_id'] = shooter.id
            s['shooter_name'] = shooter.user.name
        del s['shoot_data_r']
        if to_camel:
            s = self.to_camel(s)
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
    def page(cls, params):
        page_num = int(params.get('pageNum', 1))
        page_size = int(params.get('pageSize', 10))

        query = db.session.query(TrainRecord).join(Shooter).join(User)

        if cls.filter_dict(params).get('id') is not None:
            query = query.filter(TrainRecord.id == params.get('id'))
        if params.get('shooterId') is not None and len(params.get('shooterId')) > 0:
            query = query.filter(Shooter.id == params.get('shooterId'))
        if params.get('shooterName') is not None:
            query = query.filter(User.name.like('%' + params.get('shooterName') + '%'))

        range_param = cls.filter_range_params(dict(params))
        query = cls.range_query_snippet(query, range_param)

        page = query.paginate(page=page_num, per_page=page_size)
        return page

    @classmethod
    def update(cls, data: dict, key='dataId', err_msg='未找到射击数据'):
        super().update(data, key, err_msg)

    @classmethod
    def delete(cls, model_id, err_msg='未找到射击数据'):
        super().delete(model_id, err_msg)
