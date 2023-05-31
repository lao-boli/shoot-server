import datetime

import yaml
import json


class YamlUtil:

    @staticmethod
    def read_yaml(path):
        with open(path, encoding="utf-8") as f:
            result = f.read()
            result = yaml.load(result, Loader=yaml.FullLoader)
            return result

    @staticmethod
    def write_yaml(path, data):
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, Dumper=yaml.SafeDumper, sort_keys=False, allow_unicode=True)



def generate_final(excludes: list):
    empty: dict = YamlUtil.read_yaml("../doc/empty.yml")

    import os
    # 定义目录路径
    dir_path = os.path.normpath('../doc')

    # 遍历目录下所有文件
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            # 获取文件名
            if file.startswith('api'):
                file_name = os.path.join(root, file)
                api_dict = YamlUtil.read_yaml(file_name)
                empty['paths'].update(api_dict['paths'])
                empty['definitions'].update(api_dict['definitions'])
    YamlUtil.write_yaml("../doc/final.yml", empty)


generate_final([])

from flaskr.models import *
from StyleFormatter import *

convert_map = {
    str: 'string',
    int: 'integer',
    float: 'number',
    datetime.datetime: 'string'

}
print(convert_map[str])


def generate_model(model: Base):
    columns = model.__table__.columns

    model_data = {"type": 'object', 'properties': {}}
    for column in columns:
        # 获取每个字段上定义的 comment 信息
        model_data['properties'][snake_to_camel(column.name)] = {"type": convert_map[column.type.python_type],
                                                                 "description": column.comment}
        # print(f'{column.name}: {column.comment}: {convert_map[column.type.python_type]}')

    data = json.dumps(model_data, indent=1, ensure_ascii=False)
    print(data)
    return model_data


def generate_model_and_write(model: Base, path: str):
    data = generate_model(model)
    YamlUtil.write_yaml(f"../doc/{path}.yml", data)


def summary():
    pass


# generate_model(ShootData())
# generate_model_and_write(ShootData(), 'shootData')
# record = generate_model(TrainRecord())


