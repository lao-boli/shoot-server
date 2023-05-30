import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Double, false, ForeignKey
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from .base import Base, db
from flaskr.exception import ResultError


class ShootData(Base):
    __tablename__ = 'shoot_data'
    __table_args__ = {'comment': '射击数据表'}
    id = Column(Integer, primary_key=True, comment='射击数据id')
    record_id = Column(String(255), ForeignKey('train_record.id'), comment='训练记录id')

    sequence = Column(Integer, nullable=False, comment='弹序')
    shoot_time = Column(DateTime, comment='射击时间')
    aim_ring_number = Column(Double, nullable=False, comment='命中环数')
    hit_ring_number = Column(Double, nullable=False, comment='瞄准环数')
    gun_shaking = Column(Integer, nullable=False, comment='据枪晃动量')
    gun_shaking_rate = Column(Integer, nullable=False, comment='据枪晃动速率')
    fire_shaking_rate = Column(Integer, nullable=False, comment='击发晃动量')
    fire_shaking = Column(Integer, nullable=False, comment='击发晃动速率')
    shooting_accuracy = Column(Double, nullable=False, comment='射击精确性')
    gun_stability = Column(Double, nullable=False, comment='据枪稳定性')
    fire_stability = Column(Double, nullable=False, comment='击发稳定性')
    score = Column(Double, nullable=False, comment='本次射击成绩')

    @classmethod
    def update(cls, data: dict, key='dataId', err_msg='未找到射击数据'):
        super().update(data, key, err_msg)

    @classmethod
    def delete(cls, model_id, err_msg='未找到射击数据'):
        super().delete(model_id, err_msg)
