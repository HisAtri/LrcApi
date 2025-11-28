import logging

from utils import tag
from utils.data_types import MusicTag, MusicTagRequest
from utils.exceptions import (
    MusicFileNotFoundError,
    MusicTagError,
    InsufficientFilePermissionError,
    UnsupportedMetadataTypeError
)

logger = logging.getLogger(__name__)


def request_to_music_tag(request: MusicTagRequest) -> MusicTag:
    """
    将 FastAPI 请求模型转换为后端音乐标签模型
    注意：MusicTagRequest 使用 'title'，而 MusicTag 使用 'tracktitle'
    
    :param request: MusicTagRequest 对象
    :return: MusicTag 对象
    """
    return MusicTag(
        tracktitle=request.title if request.title is not None else None,
        artist=request.artist,
        album=request.album,
        year=request.year,
        lyrics=request.lyrics,
        artwork=request.artwork
    )


def music_tag_to_response(music_tag_obj: MusicTag) -> dict:
    """
    将后端音乐标签模型转换为 API 响应格式
    注意：将 'tracktitle' 转换为 'title' 以保持 API 一致性
    
    :param music_tag_obj: MusicTag 对象
    :return: 响应字典
    """
    data = music_tag_obj.model_dump()
    # 将 tracktitle 转换为 title
    data['title'] = data.pop('tracktitle', None)
    return data


def write_music_tag(request: MusicTagRequest) -> dict:
    """
    写入音乐文件标签
    
    :param request: MusicTagRequest 对象
    :return: 操作结果和更新后的标签
    :raises MusicFileNotFoundError: 文件不存在
    :raises InsufficientFilePermissionError: 文件权限不足
    :raises UnsupportedMetadataTypeError: 不支持的元数据类型
    :raises MusicTagError: 标签操作失败
    """
    logger.info(f"写入音乐标签: {request.path}")
    
    try:
        # 转换请求为后端模型
        music_tag_obj = request_to_music_tag(request)
        
        # 获取非 None 的字段进行写入
        tags_to_write = music_tag_obj.get_non_none_fields()
        
        if not tags_to_write:
            logger.info("没有需要写入的标签")
            # 返回当前标签
            current_tags = tag.read(request.path)
            return {
                "status": "unchanged",
                "message": "No tags to write",
                "tags": music_tag_to_response(current_tags)
            }
        
        # 写入标签
        tag.write(tags_to_write, request.path)
        
        # 读取更新后的标签
        updated_tags = tag.read(request.path)
        
        return {
            "status": "success",
            "message": "Tags updated successfully",
            "tags": music_tag_to_response(updated_tags)
        }
    except (MusicFileNotFoundError, InsufficientFilePermissionError, UnsupportedMetadataTypeError, MusicTagError):
        raise
    except Exception as e:
        logger.error(f"写入音乐标签失败: {e}")
        raise MusicTagError(detail=str(e))
