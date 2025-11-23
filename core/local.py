import os

from utils.value import LyricResponse, SearchParams
from utils.data import hash_data


def read_file(path: str) -> str:
    """
    使用多种编码读取Lrc文本文件

    :param path: 文件路径
    :type path: str
    :return: 文件内容
    :rtype: str
    """
    encodings: list[str] = [
        'utf-8-sig',
        'utf-8',
        'gbk',
        'gb2312', 
        'big5',
        'utf-16',
        'shift-jis',
        'euc-kr'
    ]
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue

    tried_encodings = ", ".join(encodings)
    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        0,
        f"Failed to decode file {path} with any of the tried encodings: {tried_encodings}",
    )

def lrc_files(path: str) -> list[str]:
    """
    将音乐路径转换为可能的歌词路径。

    例如:
    'music/song.mp3' -> ['music/song.mp3.lrc', 'music/song.lrc']
    'archive/beat'   -> ['archive/beat.lrc']

    :param path: 音乐路径
    :type path: str
    :return: 可能的歌词路径列表
    :rtype: list[str]
    """
    if not path:
        return []
    
    # 1. 直接在原始路径末尾添加 .lrc
    path_appended = path + ".lrc"

    # 2. 将原始路径的扩展名替换为 .lrc
    file_root, _ = os.path.splitext(path)
    path_replaced = file_root + ".lrc"

    # 使用 set 自动处理重复的情况
    possible_paths = {path_appended, path_replaced}
    return list(possible_paths)


def get_local_lyric(search_params: SearchParams) -> LyricResponse:
    """
    获取本地歌词

    :param search_params: 搜索参数
    :type search_params: SearchParams
    :return: 歌词响应
    :rtype: LyricResponse
    """
    _path: str = search_params.get("path", "")
    if not _path:
        return None

    path = os.path.abspath(_path)
    lrc_paths: list[str] = lrc_files(path)
    for lrc_path in lrc_paths:
        if os.path.exists(lrc_path) and os.path.isfile(lrc_path) and (lyrics:=read_file(lrc_path)):
            return LyricResponse(
                id=f"local:{hash_data(search_params.title, search_params.artist, search_params.album, lyrics)}",
                title=search_params.title,
                artist=search_params.artist,
                album=search_params.album,
                lyrics=lyrics
            )
    return None
    