import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, Double, false, ForeignKey
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from .base import Base, db
from flaskr.exception import ResultError
from .user import User


class Shooter(Base):
    __tablename__ = 'shooter'
    __table_args__ = {'comment': '射手表'}
    id = Column(String(255), primary_key=True, comment='射手id')
    username = Column(String(255), ForeignKey('user.username'), comment='射手账号名')

    train_record_r = db.relationship('TrainRecord', backref='shooter')
    train_record_list = []

    def serialize(self):
        s = super().serialize()
        s['train_record_list'] = self.serialize_list(self.train_record_list)
        if s['user'] is not None:
            user: User = s['user']
            s['name'] = user.name
            del s['user']
        del s['train_record_r']
        return s

    @classmethod
    def page_to_dict(cls, params):
        pagination = cls.page(params)
        return {
            'total': pagination.total,
            'pageNum': pagination.page,
            'pageSize': pagination.per_page,
            'list': cls.serialize_list(pagination.items)}

    @classmethod
    def get_by_shooter_id(cls, shooter_id):
        shooter = super().get_by({id: shooter_id})
        shooter.train_record_list = shooter.train_record_r.all()
        return shooter

    @classmethod
    def page(cls, params):
        page_num = int(params.get('pageNum', 1))
        page_size = int(params.get('pageSize', 10))

        query = db.session.query(Shooter).join(User)

        if cls.filter_dict(params).get('id') is not None:
            query = query.filter(Shooter.id == params.get('id'))
        if params.get('name') is not None:
            query = query.filter(User.name.like('%' + params.get('name')+'%'))
        if params.get('username') is not None:
            query = query.filter(User.username == params.get('username'))

        page = query.paginate(page=page_num, per_page=page_size)
        return page

    @classmethod
    def update(cls, data: dict, key='id', err_msg='未找到射手'):
        shooter: Shooter = cls.query.get(data.get(key))
        if shooter is None:
            raise ResultError(message=err_msg)

        shooter_data = cls.filter_dict(data, exclude=[key])
        for key, value in shooter_data.items():
            setattr(shooter, key, value)

        user_data = User.filter_dict(data)
        for key, value in user_data.items():
            setattr(shooter.user, key, value)

        db.session.commit()
        return shooter

    @classmethod
    def delete(cls, model_id, err_msg='未找到射手'):
        super().delete(model_id, err_msg)
