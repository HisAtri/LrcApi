"""
此模块用于定义项目数据类型
"""
from typing import TypedDict

class JsonApiResponse(TypedDict):
    id: str
    title: str
    artist: str
    lyrics: str
