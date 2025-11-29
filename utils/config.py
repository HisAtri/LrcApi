"""
配置模块 - 读取启动参数和环境变量
优先级: 启动参数 > 环境变量 > 默认值
"""
import argparse
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """应用配置"""
    auth: Optional[str]
    host: str
    port: int
    debug: bool
    romaji: bool  # 是否为日语歌词自动合并罗马字注音


def _get_env_bool(key: str, default: bool = False) -> bool:
    """从环境变量获取布尔值"""
    value = os.environ.get(key, "").lower()
    if value in ("true", "1", "yes", "on"):
        return True
    if value in ("false", "0", "no", "off"):
        return False
    return default


def _parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="LrcApi - 歌词 API 服务")
    parser.add_argument("--auth", type=str, default=None, help="API 认证密钥")
    parser.add_argument("--host", type=str, default=None, help="监听地址")
    parser.add_argument("--port", type=int, default=None, help="监听端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--romaji", action="store_true", help="开关罗马字注音")
    return parser.parse_args()


def load_config() -> Config:
    """
    加载配置
    优先级: 启动参数 > 环境变量 > 默认值
    """
    args = _parse_args()
    
    auth = args.auth
    if auth is None:
        auth = os.environ.get("API_AUTH")
    
    host = args.host
    if host is None:
        host = os.environ.get("API_HOST", "127.0.0.1")
    
    port = args.port
    if port is None:
        port = int(os.environ.get("API_PORT", "28883"))
    
    debug = args.debug or _get_env_bool("DEBUG", False)
    romaji = args.romaji or _get_env_bool("ROMAJI", False)
    
    return Config(
        auth=auth,
        host=host,
        port=port,
        debug=debug,
        romaji=romaji
    )


# 全局配置实例（延迟加载）
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = load_config()
    return _config

