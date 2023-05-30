import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Double, false, ForeignKey
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from .base import Base, db
from flaskr.exception import ResultError


class Trainer(Base):
    __tablename__ = 'trainer'
    __table_args__ = {'comment': '教练员表'}
    id = Column(String(255), primary_key=True, comment='教练员id')
    username = Column(String(255), ForeignKey('user.username'), comment='教练员账号')

    # user_r = db.relationship('User', uselist=False, backref='Trainer')
    account = {}

    def serialize(self):
        s = super().serialize()
        s['train_record_list'] = self.serialize_list(self.order_list)
        del s['train_record_r']
        return s

    @classmethod
    def get_by_trainer_id(cls, params):
        """

        :param params: {trainer_id: val}
        :return:
        """
        trainer = super().get_by(params)
        trainer.account = trainer.user_r.one()
        return trainer

    @classmethod
    def list(cls, params):
        records = super().list(params)
        for record in records:
            record.train_record_list = record.train_record_r.all()
        return records

    @classmethod
    def update(cls, data: dict, key='id', err_msg='未找到教练'):
        super().update(data, key, err_msg)

    @classmethod
    def delete(cls, model_id, err_msg='未找到教练'):
        super().delete(model_id, err_msg)
