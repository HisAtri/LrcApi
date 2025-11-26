"""
此模块用于定义项目数据类型
"""
from typing import TypedDict, NotRequired, Optional
from pydantic import BaseModel, Field

class LyricResponse(BaseModel):
    id: str = Field(..., description="歌词ID")
    title: str = Field(..., description="歌曲标题")
    artist: str = Field(..., description="艺术家名称")
    album: str = Field(..., description="专辑名称")
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

class MusicTagRequest(BaseModel):
    """FastAPI请求模型"""
    path: str = Field(..., description="文件路径")
    title: Optional[str|bool|None] = Field(None, description="歌曲标题")
    artist: Optional[str|bool|None] = Field(None, description="艺术家名称")
    album: Optional[str|bool|None] = Field(None, description="专辑名称")
    year: Optional[int|str|bool|None] = Field(None, description="年份")
    lyrics: Optional[str|bool|None] = Field(None, description="歌词")
    artwork: Optional[str|bool|None] = Field(None, description="封面图片Base64")

class MusicTag(BaseModel):
    """后端音乐标签数据模型，歌曲标题的键与FastAPI模型有区别"""
    tracktitle: Optional[str] = Field(None, description="歌曲标题")
    artist: Optional[str] = Field(None, description="艺术家名称")
    album: Optional[str] = Field(None, description="专辑名称")
    year: Optional[int | str] = Field(None, description="年份")
    lyrics: Optional[str] = Field(None, description="歌词")
    artwork: Optional[str] = Field(None, description="封面图片Base64")

    model_config = {"extra": "ignore"}  # 忽略额外字段
    
    @classmethod
    def get_tag_map(cls) -> dict[str, str]:
        """获取标签名到中文描述的映射"""
        return {
            'tracktitle': '曲目标题',
            'artist': '艺术家',
            'album': '专辑',
            'year': '年份',
            'lyrics': '歌词',
            'artwork': '封面图片Base64'
        }
    
    def get_non_none_fields(self) -> dict:
        """获取所有非None的字段"""
        return {k: v for k, v in self.model_dump().items() if v is not None}