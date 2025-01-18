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
parser.add_argument('--ip', type=str, default='*', help='服务器监听IP，默认*')
parser.add_argument('--token', type=str, default='', help='用于翻译歌词的API Token')
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
        self.token = os.environ.get('API_TOKEN', None)
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
        self.version = "1.5.7"

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
        self.version = "1.5.7"
        self.debug = kw_args.debug

    def __invert__(self):
        """
        JSON: config/config.json
        YAML: config/config.yaml

        default: YAML
        """
        # 1. 首先用默认值初始化
        self.__data = self.__default.copy()
        
        # 2. 加载配置文件，使用update而不是直接赋值
        for loader in (self.__load_json, self.__load_yaml):
            data = loader()
            if isinstance(data, dict):
                self.__data.update(data)
                break
        
        # 3. 加载环境变量
        self.__load_env()
        
        # 4. 最后加载命令行参数（最高优先级）
        self.__load_arg()

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
        
    def __load_env(self):
        auth = os.environ.get('API_AUTH', None)
        port = os.environ.get('API_PORT', None)
        token = os.environ.get('API_TOKEN', None)
        if auth:
            self.__data["auth"] = {auth: "all"}
        if port:
            # 确保 server 是一个字典
            if not isinstance(self.__data.get("server"), dict):
                self.__data["server"] = {"ip": "*"}
            self.__data["server"]["port"] = port
        if token:
            self.__data["token"] = token

    def __load_arg(self):
        auth = kw_args.auth
        port = kw_args.port
        ip = kw_args.ip
        token = kw_args.token
        logger.info(f"Auth: {auth}; Port: {port}; IP: {ip}")
        if auth:
            self.__data["auth"] = {auth: "all"}
        if port:
            if not isinstance(self.__data.get("server"), dict):
                self.__data["server"] = {"ip": "*"}
            self.__data["server"]["port"] = port
        if ip:
            if not isinstance(self.__data.get("server"), dict):
                self.__data["server"] = {"ip": "*"}
            self.__data["server"]["ip"] = ip
        if token:
            self.__data["token"] = token
        #logger.info(f"Final config data: {self.__data}")

    def __call__(self, *args):
        data = self.__data
        default = self.__default
        for key in args:
            if key in data:
                data = data[key]
            elif key in default:
                data = default[key]
            else:
                return None
        return data
    
args = Args(default=DEFAULT_DATA)
~args  # 初始化配置

if __name__ == '__main__':
    default: dict = {
        "server": {
            "ip": "*",
            "port": 28883
        },
        "auth": {}
    }
    config = Args(default=default)
    ~config
    print(config("server", "port"))
