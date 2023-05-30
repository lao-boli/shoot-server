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
            yaml.dump(data, f, Dumper=yaml.SafeDumper,sort_keys=False,allow_unicode=True)


empty: dict = YamlUtil.read_yaml("../doc/empty.yml")
json_list = json.dumps(empty, indent=1, ensure_ascii=False)
print(json_list)

shooter = YamlUtil.read_yaml("../doc/shooter.yml")
empty['paths'].update(shooter['paths'])
empty['definitions'].update(shooter['definitions'])
YamlUtil.write_yaml("../doc/final.yml",empty)
json_list2 = json.dumps(empty, indent=1, ensure_ascii=False)
print(json_list2)