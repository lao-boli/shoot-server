import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.exc import IntegrityError, NoResultFound
from werkzeug.security import generate_password_hash
from .base import Base, db
from flaskr.exception import ResultError


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, comment='主键')
    create_time = Column(DateTime, comment='创建时间')
    name = Column(String(50), nullable=True, comment='用户姓名')
    username = Column(String(255), unique=True, nullable=True, comment='账号名')
    password = Column(String(300), nullable=True, comment='密码')
    role_id = Column(String(50), comment='角色ID,(admin,trainer,shooter)')
    age = Column(Integer, comment='用户年龄')

    shooter_r = db.relationship('Shooter', uselist=False, backref='user')
    trainer_r = db.relationship('Trainer', uselist=False, backref='user')

    def serialize(self):
        s = super().serialize()
        del s['shooter_r']
        del s['trainer_r']
        return s

    @classmethod
    def get_by_username(cls, username):
        try:
            user = cls.query.filter_by(username=username).one()
            return user
        except NoResultFound:
            return None


    @classmethod
    def update(cls, data: dict, key='userId', err_msg='未找到用户'):
        super().update(data, key, err_msg)

    @classmethod
    def delete(cls, model_id, err_msg='未找到用户'):
        super().delete(model_id, err_msg)
