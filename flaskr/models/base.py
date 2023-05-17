import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError

from flaskr.exception import ResultError
from .serializer import Serializer

db = SQLAlchemy()

logger = logging.getLogger(__name__)

class Base(db.Model, Serializer):
    # 忽略基类的主键
    __abstract__ = True

    @classmethod
    def get_db(cls):
        return db

    @classmethod
    def init_query(cls, params: dict) -> db.Query:
        query: db.Query = cls.query

        # 查询相等字段参数,e.g: username=username
        column_params = cls.filter_dict(dict(params))
        query = query.filter_by(**column_params)

        # 查询范围字段参数,e.g: age>=min_age
        range_param = cls.filter_range_params(dict(params))
        query = cls.range_query_snippet(query, range_param)

        # 排序字段
        query = cls.order_by_snippet(params, query)

        return query

    @classmethod
    def order_by_snippet(cls, params, query):
        order_by = params.get('orderBy')
        if order_by:  # 如果排序字段不为空，则按该字段排序
            split = order_by.split(' ', 1)
            column: str = split[0]
            order: str = split[1].strip() if len(split) == 2 else 'asc'
            if hasattr(cls, column):
                if order == 'desc':
                    query = query.order_by(getattr(cls, column).desc())
                else:
                    query = query.order_by(getattr(cls, column).asc())
        return query

    @classmethod
    def get_by_id(cls, model_id):
        return cls.query.get(model_id)

    @classmethod
    def get_by(cls, param: dict):
        query: db.Query = cls.query
        return query.filter_by(**param).one()

    @classmethod
    def list(cls, params):
        query = cls.init_query(params)
        users = query.all()
        return users

    @classmethod
    def page(cls, params):
        page_num = int(params.get('pageNum', 1))
        page_size = int(params.get('pageSize', 10))
        query = cls.init_query(params)
        page = query.paginate(page=page_num, per_page=page_size)
        return page

    @classmethod
    def page_to_dict(cls, params):
        pagination = cls.page(params)
        return {
            'total': pagination.total,
            'pageNum': pagination.page,
            'pageSize': pagination.per_page,
            'items': cls.serialize_list(pagination.items)}

    @classmethod
    def add(cls, data):
        filtered_data = cls.filter_dict(data)
        model = cls(**filtered_data)
        try:
            db.session.add(model)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if 'Duplicate entry' in str(e):
                raise ResultError(message='键冲突')
            elif 'foreign key' in str(e):
                raise ResultError(message='外键所指的记录不存在')
            elif 'cannot be null' in str(e):
                raise ResultError(message='非空字段为空')
            else:
                logger.warning(e)
                raise ResultError(message='Database IntegrityError')
        except DataError as e:
            db.session.rollback()
            logger.warning(e)
            raise ResultError(message='数据格式错误')
        except DatabaseError as e:
            db.session.rollback()
            logger.error(e)
            raise ResultError(message='数据库错误')
        return model

    @classmethod
    def update(cls, data: dict, key='id', err_msg='未找到记录'):
        model = cls.query.get(data.get(key))
        if model is None:
            raise ResultError(message=err_msg)

        filtered_data = cls.filter_dict(data, exclude=[key])
        # 将过滤后的数据赋值到对应的属性
        for key, value in filtered_data.items():
            setattr(model, key, value)
        db.session.commit()
        return model

    @classmethod
    def delete(cls, model_id, err_msg='未找到记录'):
        model = cls.query.get(model_id)
        if model is None:
            raise ResultError(message=err_msg)
        db.session.delete(model)
        db.session.commit()

    @classmethod
    def filter_dict(cls, data: dict, exclude=[]):
        """
        过滤参数
        :param data: 查询参数字典
        :param exclude: 要排除过滤的参数键名
        :return: 参数字典中，存在于model属性的参数
        """
        return {k: v for k, v in data.items() if k in cls.__table__.columns.keys() and k not in exclude}

    @classmethod
    def filter_range_params(cls, data: dict, exclude=[]):
        """
        过滤范围参数
        :param data: 查询参数字典
        :param exclude: 要排除过滤的参数键名
        :return: 参数字典中，以min、max、start、end开头的参数字典
        """
        return {
            k: v for k, v in data.items()
            if (k.startswith('min') or k.startswith('max') or k.startswith('start') or k.startswith('end'))
               and k not in exclude
        }

    @classmethod
    def range_query_snippet(cls, query: db.Query, params: dict):
        """
        为query拼接范围查询
        :param query: query object
        :param params: 范围查询参数
        :return: 拼接完成范围查询filter后的query对象
        """
        for k, v in params.items():
            split = k.split('_', 1)
            prefix = split[0]
            column = split[1]
            if not hasattr(cls, column):
                continue
            # number
            if prefix == 'min':
                query = query.filter(getattr(cls, column) >= int(v))
            if prefix == 'max':
                query = query.filter(getattr(cls, column) <= int(v))
            # time
            if prefix == 'start':
                query = query.filter(getattr(cls, column) >= v)
            if prefix == 'end':
                query = query.filter(getattr(cls, column) <= v)
        return query
