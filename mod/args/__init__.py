import argparse
import json
import yaml
import logging
import os

logger = logging.getLogger(__name__)

# 启动参数解析器
parser = argparse.ArgumentParser(description="启动LRCAPI服务器")
# 添加一个 `--port` 参数，默认值28883
parser.add_argument('--port', type=int, default=28883, help='应用的运行端口，默认28883')
parser.add_argument('--auth', type=str, default='', help='用于验证Header.Authentication字段，建议纯ASCII字符')
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
kw_args, unknown_args = parser.parse_known_args()
arg_auths: dict = {kw_args.auth: "rwd"} if kw_args.auth else None


# 按照次序筛选首个非Bool False（包括None, '', 0, []等）值；
# False, None, '', 0, []等值都会转化为None
def first(*args):
    """
    返回第一个非False值
    :param args:
    :return:
    """
    result = next(filter(lambda x: x, args), None)
    return result


class DefaultConfig:
    def __init__(self):
        self.ip = '*'
        self.port = 28883


class ConfigFile:
    """
    读取json配置文件
    """

    def __init__(self):
        json_config = {
            "server": {
                "ip": "*",
                "port": 28883
            },
            "auth": {}
        }
        file_path = os.path.join(os.getcwd(), "config", "config.json")
        try:
            with open(file_path, "r+") as json_file:
                json_config = json.load(json_file)
        except FileNotFoundError:
            # 如果文件不存在，则创建文件并写入初始配置
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(file_path, "w+") as json_file:
                json.dump(json_config, json_file, indent=4)
        self.auth: dict = json_config.get("auth", {})
        self.server = json_config.get("server", {})
        self.port = self.server.get("port", 0)
        self.ip = self.server.get("ip", "*")


# 环境变量定义值
class EnvVar:
    def __init__(self):
        self.auth = os.environ.get('API_AUTH', None)
        self.port = os.environ.get('API_PORT', None)
        self.auths = None
        if self.auth:
            self.auths: dict = {
                self.auth: "all"
            }


env_args = EnvVar()
config_args = ConfigFile()
default = DefaultConfig()


# 按照优先级筛选出有效值
class GlobalArgs:
    def __init__(self):
        self.auth: dict = first(env_args.auths, arg_auths, config_args.auth)
        if type(self.auth) is not dict:
            self.auth: dict = {}
        self.port = first(env_args.port, kw_args.port, config_args.port, default.port)
        self.ip = first(config_args.ip, default.ip)
        self.debug = kw_args.debug
        self.version = "1.5.4"

    def valid(self, key) -> bool:
        """
        返回该key是否有效
        :param key:
        :return:
        """
        return key in self.auth.keys()

    def permission(self, key) -> str:
        """
        返回该key的权限组字符串
        :param key:
        :return:
        """
        return self.auth.get(key, '')

DEFAULT_DATA = {
            "server": {
                "ip": "*",
                "port": 28883
            },
            "auth": {}
        }

class Args():
    def __init__(self, data=None, default=None):
        self.__data: dict = data
        self.__default: dict = default or {}

    def __invert__(self):
        return self.__data

    def __get(self, key: str) -> 'Args':
        # 如果不是字典，则返回Args包装的None
        if not isinstance(self.__data, dict):
            return Args()
        else:
            # 如果key不存在，则返回Args包装的None
            if key not in self.__data.keys():
                return Args()
            # 如果key对应的值是字典，则返回Args包装的字典，默认值从__default中获取
            if isinstance(self.__data[key], dict):
                return Args(data=self.__data[key], default=self.__default.get(key, {}))
            # 如果key对应的值不是字典，则返回Args包装的值
            return Args(data=self.__data[key])

    def __set_default(self, default_data: dict):
        self.__default = default_data

    def __call__(self):
        """
        JSON: config/config.json
        YAML: config/config.yaml

        default: YAML
        """
        for loader in (self.__load_json, self.__load_yaml):
            data = loader()
            if isinstance(data, dict):
                self.__data = data
                return
            # 如果没有读取到有效数据，则使用默认数据
            self.__data = self.__default
            # 写入默认数据
            directory = os.path.join(os.getcwd(), "config")
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, "config.yaml")
            with open(file_path, "w+") as yaml_file:
                yaml.dump(DEFAULT_DATA, yaml_file)

    @staticmethod
    def __load_json() -> dict|None:
        file_path = os.path.join(os.getcwd(), "config", "config.json")
        try:
            with open(file_path, "r+") as json_file:
                return json.load(json_file)
        # 解析错误
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    @staticmethod
    def __load_yaml() -> dict|None:
        file_path = os.path.join(os.getcwd(), "config", "config.yaml")
        try:
            with open(file_path, "r+") as yaml_file:
                return yaml.safe_load(yaml_file)
        except (yaml.YAMLError, FileNotFoundError):
            return None

    def __getattribute__(self, item):
        if item.startswith('_'):
            return super().__getattribute__(item)
        return self.__get(item)

    def __str__(self):
        return str({
            "data": self.__data,
            "default": self.__default
        })

if __name__ == '__main__':
    default: dict = {
        "server": {
            "ip": "*",
            "port": 28883
        },
        "auth": {}
    }
    config = Args(default=default)
    config()
    print(~config.server)
    print(~config.server.port)
    print(~config.auth)
    print(~config.auth.admin)