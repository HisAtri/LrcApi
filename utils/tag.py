import base64
import os
import io
import logging
from typing import Optional, Union

from PIL import Image
from pydantic import ValidationError

from utils import music_tag
from utils.value import MusicTag

logger = logging.getLogger(__name__)


def dump_b64(album_art: music_tag.file.MetadataItem) -> str:
    """
    以图片加载MetadataItem对象并进行base64编码
    :param album_art: 专辑封面元数据项
    :return: Base64编码的图片字符串
    """
    logger.debug("开始处理专辑封面图片的base64编码")
    try:
        artwork = album_art.values[0]
        img_data = artwork.data
        img_format = artwork.format
        img = Image.open(io.BytesIO(img_data))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img_format)
        img_base64 = base64.b64encode(img_byte_arr.getvalue())
        logger.debug(f"图片编码完成，格式: {img_format}")
        return img_base64.decode()
    except Exception as e:
        logger.error(f"处理专辑封面时发生错误: {str(e)}")
        raise


def _resolve_file_path(file: Union[str, any]) -> Optional[str]:
    """
    解析文件路径
    :param file: 文件路径字符串或文件对象
    :return: 文件路径字符串或None
    """
    if isinstance(file, str):
        return file
    if hasattr(file, 'name'):
        return file.name
    return None


def write(tags: Union[MusicTag, dict], file: Union[str, any]) -> None:
    """
    写入音乐标签到文件
    :param tags: MusicTag对象或字典，包含Tags数据
    :param file: 文件路径字符串或file-like对象
    :return: None
    :raises TypeError: tags类型不正确
    :raises FileNotFoundError: 文件不存在
    :raises ValidationError: 标签数据验证失败
    """
    logger.info("开始写入音乐标签")
    
    # 将字典转换为MusicTag对象进行验证
    if isinstance(tags, dict):
        try:
            music_tag_obj = MusicTag.model_validate(tags)
        except ValidationError as e:
            logger.error(f"标签数据验证失败: {e}")
            raise
    elif isinstance(tags, MusicTag):
        music_tag_obj = tags
    else:
        err_msg = f'Tags should be MusicTag or dict, but {type(tags).__name__} found.'
        logger.error(err_msg)
        raise TypeError(err_msg)

    file_path = _resolve_file_path(file)
    if not file_path or not os.path.exists(file_path):
        err_msg = f'File {file_path} does not exist or path is invalid.'
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    logger.debug(f"准备写入文件: {file_path}")
    music_file_obj = music_tag.load_file(file)
    
    tag_map = MusicTag.get_tag_map()
    
    # 使用model_dump获取所有字段
    for tag_name, tag_value in music_tag_obj.model_dump().items():
        if tag_name == "artwork" and tag_value:
            logger.debug("处理专辑封面数据")
            artwork_raw: bytes = base64.b64decode(tag_value)
            artwork = music_tag.file.Artwork(artwork_raw)
            music_file_obj[tag_name] = artwork
        elif tag_name in tag_map and tag_value:
            tag_desc = tag_map.get(tag_name, tag_name)
            logger.debug(f"写入标签 {tag_desc}: {tag_value}")
            music_file_obj[tag_name] = tag_value
        elif tag_value is False:
            logger.debug(f"删除标签: {tag_name}")
            del music_file_obj[tag_name]
        elif tag_value is None:
            # 跳过None值的字段
            continue
        else:
            logger.warning(f"跳过无效的标签: {tag_name}")
            continue

    music_file_obj.save()
    logger.debug("音乐标签写入完成")


def read(file: Union[str, any]) -> MusicTag:
    """
    读取音乐文件标签
    :param file: 文件路径字符串或file-like对象
    :return: MusicTag对象
    """
    file_path = _resolve_file_path(file)
    
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"文件不存在或路径无效: {file_path}")
        return MusicTag()
        
    logger.debug(f"开始读取音乐文件标签: {file_path}")
    result = {}
    
    try:
        tag_map = MusicTag.get_tag_map()
        music_file = music_tag.load_file(file_path)
        
        for tag_name in tag_map.keys():
            logger.debug(f"读取标签 {tag_map[tag_name]}")
            if tag_name == "artwork":
                try:
                    result[tag_name] = dump_b64(music_file.resolve(tag_name))
                except Exception:
                    result[tag_name] = None
            else:
                value = music_file.resolve(tag_name)
                result[tag_name] = str(value) if value else None
        
        logger.debug("音乐标签读取完成")
        return MusicTag.model_validate(result)
    except Exception as e:
        logger.error(f"读取标签时发生错误: {str(e)}")
        raise
