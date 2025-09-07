from fastapi import APIRouter, Depends
from typing import Optional
from utils.value import SearchParams

from controller.lyric import get_lyric
from utils.response_codes import LyricsNotFoundError

router = APIRouter()

@router.get("/lyric")
def get_lyric(params: SearchParams = Depends()) -> str:
    """
    查询并返回text/lrc歌词文本
    """
    if result:=get_lyric(params, fast=True):
        return result[0].lyrics
    elif params.fast:
        return LyricsNotFoundError()
    elif result:=get_lyric(params, fast=False):
        return result[0].lyrics
        