import base64
import os
import io
import logging

from PIL import Image

from mod import music_tag

logger = logging.getLogger(__name__)

TAG_MAP = {
    'tracktitle': '曲目标题',
    'artist': '艺术家',
    'album': '专辑',
    'year': '年份',
    'lyrics': '歌词',
    'artwork': '封面图片Base64'
}


def dump_b64(album_art: music_tag.file.MetadataItem) -> str:
    """
    以图片加载MetadataItem对象并进行base64编码
    :param album_art:
    :return:
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


def write(tags: dict, file: any) -> None:
    """
    :param tags: 字典，包含Tags数据，详见TAG_MAP
    :param file: string, file-like object, io.StringIO, etc.
    :return: None
    """
    logger.info(f"开始写入音乐标签")
    
    if not isinstance(tags, dict):
        err_msg = f'Tags should be dict, but {type(tags).__name__} found.'
        logger.error(err_msg)
        raise TypeError(err_msg)

    file_path = file if isinstance(file, str) else (file.name if hasattr(file, 'name') else None)
    if not file_path or not os.path.exists(file_path):
        err_msg = f'File {file_path} does not exist or path is invalid.'
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    logger.debug(f"准备写入文件: {file_path}")
    music_file_obj = music_tag.load_file(file)
    
    for tag_name, tag_value in tags.items():
        if tag_name == "artwork" and tag_value:
            logger.debug("处理专辑封面数据")
            artwork_raw: bytes = base64.b64decode(tag_value)
            artwork = music_tag.file.Artwork(artwork_raw)
            music_file_obj[tag_name] = artwork
        elif tag_name in TAG_MAP and tag_value:
            logger.debug(f"写入标签 {TAG_MAP[tag_name]}: {tag_value}")
            music_file_obj[tag_name] = tag_value
        elif tag_value is False:
            logger.debug(f"删除标签: {tag_name}")
            del music_file_obj[tag_name]
        else:
            logger.warning(f"跳过无效的标签: {tag_name}")
            continue

    music_file_obj.save()
    logger.debug("音乐标签写入完成")


def read(file: any) -> dict:
    file_path = file if isinstance(file, str) else (file.name if hasattr(file, 'name') else None)
    
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"文件不存在或路径无效: {file_path}")
        return {}
        
    logger.debug(f"开始读取音乐文件标签: {file_path}")
    result = {}
    
    try:
        for tag_name, tag_desc in TAG_MAP.items():
            logger.debug(f"读取标签 {tag_desc}")
            if tag_name == "artwork":
                result[tag_name] = dump_b64(music_tag.load_file(file_path).resolve(tag_name))
            else:
                result[tag_name] = str(music_tag.load_file(file_path).resolve(tag_name))
        
        logger.debug("音乐标签读取完成")
        return result
    except Exception as e:
        logger.error(f"读取标签时发生错误: {str(e)}")
        raise


if __name__ == '__main__':
    val_tags = {
        'tracktitle': '曲目标题',
        'artist': '艺术家',
        'album': '专辑',
        'year': 2022,
        'lyrics': '歌词'
    }
    print(read(r'H:\sp\test.mp3'))
