import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from .base import Base, db
from flaskr.exception import ResultError


class Order(Base):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment='用户id')
    product_name = db.Column(db.String(50), comment='产品名称')
    product_price = db.Column(db.Float, comment='产品价格')

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).one()

    @classmethod
    def update(cls, data: dict, key='orderId', err_msg='未找到订单'):
        super().update(data, key, err_msg)

    @classmethod
    def delete(cls, model_id, err_msg='未找到订单'):
        super().delete(model_id, err_msg)
