from core.local import get_local_lyric
from utils.value import SearchParams, LyricResponse

from typing import List

def get_lyric(params: SearchParams, fast: bool = False) -> List[LyricResponse]:
    """
    获取歌词
    """
    result: List[LyricResponse] = []
    result.append(get_local_lyric(params))
    if fast or params.fast:
        return result
    # TODO: 网络搜索部分接口
    return result
