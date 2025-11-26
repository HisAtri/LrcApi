from typing import List

from fastapi import APIRouter, Depends

from controller.lyric import get_lyric
from utils.value import LyricResponse, SearchParams
from utils.exceptions import LyricsNotFoundError

router = APIRouter()

@router.get("/lyric")
async def lrc_text_api(params: SearchParams = Depends()) -> str:
    """
    查询并返回text/lrc歌词文本
    """
    if result := await get_lyric(params, single=True):
        return result[0].lyrics
    raise LyricsNotFoundError()


@router.get("/jsonapi", response_model=List[LyricResponse])
async def lrc_json_api(params: SearchParams = Depends()) -> List[LyricResponse]:
    """
    批量返回 JSON 歌词列表，遵循 https://docs.lrc.cx/docs/legacy/lyrics 定义
    """
    results = await get_lyric(params)
    limit = params.limit or 0
    if limit > 0:
        results = results[:limit]
    if not results:
        raise LyricsNotFoundError()
    return results
        