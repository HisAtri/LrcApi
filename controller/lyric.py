from core.local import get_local_lyric
from utils.value import SearchParams, LyricResponse

from typing import List

def get_lyric(params: SearchParams, single: bool = False) -> List[LyricResponse]:
    """
    获取歌词
    """
    results: List[LyricResponse] = []
    if local_lyric:=get_local_lyric(params):
        results.append(local_lyric)
        if single:
            return results
    # TODO: 网络搜索部分接口
    return results
