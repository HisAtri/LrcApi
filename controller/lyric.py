from core.local import get_local_lyric
from utils.value import SearchParams, LyricResponse

from typing import List

def get_lyric(params: SearchParams, fast: bool = False) -> List[LyricResponse]:
    """
    获取歌词
    """
    result: List[LyricResponse] = []
    if local_lyric:=get_local_lyric(params):
        result.append(local_lyric)
    if fast or params.fast:
        return result
    # TODO: 网络搜索部分接口
    return result
