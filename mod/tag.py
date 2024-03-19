import base64
import os
import io

from PIL import Image

from mod import music_tag

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
    artwork = album_art.values[0]
    img_data = artwork.data
    img_format = artwork.format
    img = Image.open(io.BytesIO(img_data))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=img_format)
    # 将字节流编码为base64字符串
    img_base64 = base64.b64encode(img_byte_arr.getvalue())
    return img_base64.decode()


def write(tags: dict, file: any) -> None:
    """
    :param tags: 字典，包含Tags数据，详见TAG_MAP
    :param file: string, file-like object, io.StringIO, etc.
    :return: None
    """
    if not isinstance(tags, dict):
        raise TypeError(f'Tags should be dict, but {type(tags).__name__} found.')
    file_path = file if isinstance(file, str) else (file.name if hasattr(file, 'name') else None)
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f'File {file_path} does not exist or path is invalid.')

    music_file_obj = music_tag.load_file(file)
    for tag_name, tag_value in tags.items():
        if tag_name == "artwork" and tag_value:
            artwork_raw: bytes = base64.b64decode(tag_value)
            artwork = music_tag.file.Artwork(artwork_raw)
            music_file_obj[tag_name] = artwork
        elif tag_name in TAG_MAP and tag_value:
            music_file_obj[tag_name] = tag_value
        elif tag_value is False:
            del music_file_obj[tag_name]
        else:
            continue

    music_file_obj.save()


def read(file: any) -> dict:
    file_path = file if isinstance(file, str) else (file.name if hasattr(file, 'name') else None)
    if not file_path or not os.path.exists(file_path):
        return {}
    result = {}
    for tag_name, tag_func in TAG_MAP.items():
        if tag_name == "artwork":
            result[tag_name] = dump_b64(music_tag.load_file(file_path).resolve(tag_name))
        else:
            result[tag_name] = str(music_tag.load_file(file_path).resolve(tag_name))
    return result


if __name__ == '__main__':
    val_tags = {
        'tracktitle': '曲目标题',
        'artist': '艺术家',
        'album': '专辑',
        'year': 2022,
        'lyrics': '歌词'
    }
    print(read(r'H:\sp\test.mp3'))
