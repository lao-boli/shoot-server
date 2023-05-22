from sqlalchemy import false
from sqlalchemy.inspection import inspect

from flaskr.utils import StyleFormatter


class Serializer(object):

    def serialize(self, to_camel=False):
        res = {c: getattr(self, c) for c in inspect(self).attrs.keys()}
        if to_camel:
            StyleFormatter.snake_to_camel_dict(res)
        return res

    def to_camel(self, data_dict: dict):
        return StyleFormatter.snake_to_camel_dict(data_dict)

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
