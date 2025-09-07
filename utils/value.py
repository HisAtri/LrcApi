"""
此模块用于定义项目数据类型
"""
from typing import TypedDict, NotRequired, Optional
from pydantic import BaseModel, Field

class LyricResponse(BaseModel):
    id: str = Field(..., description="歌词ID")
    title: str = Field(..., description="歌曲标题")
    artist: str = Field(..., description="艺术家名称")
    lyrics: str = Field(..., description="歌词内容")

class SearchParams(BaseModel):
    title: Optional[str] = Field("", description="歌曲标题")
    album: Optional[str] = Field("", description="专辑名称")
    artist: Optional[str] = Field("", description="艺术家名称")
    path: Optional[str] = Field("", description="文件路径")
    # 补充参数
    duration: Optional[int] = Field(None, description="歌曲时长（秒）")
    offset: Optional[int] = Field(None, description="偏移量")
    limit: Optional[int] = Field(None, description="限制数量")
    # 查询控制
    fast: Optional[bool] = Field(False, description="在首次请求时设为True以跳过网络搜索，快速返回本地歌词")
