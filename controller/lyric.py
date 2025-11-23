import logging
from typing import List

from core.api.netease import search as netease_search
from core.local import get_local_lyric
from utils.value import SearchParams, LyricResponse

logger = logging.getLogger(__name__)


def _search_online_lyrics(params: SearchParams) -> List[LyricResponse]:
    """
    调用外部接口获取歌词
    """
    title = (params.title or "").strip()
    artist = (params.artist or "").strip()
    album = (params.album or "").strip()
    if not title:
        return []

    try:
        raw_results = netease_search(title=title, artist=artist, album=album) or []
    except Exception as exc:  # pragma: no cover - 仅日志
        logger.warning("Failed to fetch lyrics from netease: %s", exc)
        return []

    online_results: List[LyricResponse] = []
    for item in raw_results:
        lyrics = item.get("lyrics")
        if not lyrics:
            continue
        online_results.append(
            LyricResponse(
                id=f"netease:{item.get('id')}",
                title=item.get("title") or title,
                artist=item.get("artist") or artist,
                album=item.get("album") or album,
                lyrics=lyrics,
            )
        )
    return online_results


def get_lyric(params: SearchParams, single: bool = False) -> List[LyricResponse]:
    """
    获取歌词
    """
    results: List[LyricResponse] = []
    if local_lyric := get_local_lyric(params):
        results.append(local_lyric)
        if single:
            return results

    online_lyrics = _search_online_lyrics(params)
    for lyric in online_lyrics:
        results.append(lyric)
        if single:
            return results

    return results
