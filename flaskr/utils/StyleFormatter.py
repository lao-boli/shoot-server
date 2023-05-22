import re


def snake_to_camel(name):
    words = name.split('_')
    # 对第一个单词不做处理，对后面的单词进行处理
    return words[0] + ''.join(word.capitalize() for word in words[1:])

def camel_to_snake(name):
    # 使用正则表达式将首字母和大写字母分离
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # 再次使用正则表达式将大写字母和大写字母分离
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def snake_to_camel_dict(input_dict):
    result = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            # 如果 value 仍然是字典，则递归调用本函数进行转换
            value = snake_to_camel_dict(value)
        elif isinstance(value, list):
            # 如果 value 是列表，则对其中的每个元素递归调用本函数进行转换
            value = [snake_to_camel_dict(item) if isinstance(item, dict) else item for item in value]
        new_key = snake_to_camel(key)
        result[new_key] = value
    return result
def camel_to_snake_dict(input_dict):
    result = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            # 如果 value 仍然是字典，则递归调用本函数进行转换
            value = camel_to_snake_dict(value)
        elif isinstance(value, list):
            # 如果 value 是列表，则对其中的每个元素递归调用本函数进行转换
            value = [camel_to_snake_dict(item) if isinstance(item, dict) else item for item in value]
        new_key = camel_to_snake(key)
        result[new_key] = value
    return result