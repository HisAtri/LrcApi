import asyncio
import logging
from pathlib import Path
from typing import Optional

from core.api.netease import a_search as netease_search
from utils.data_types import SearchParams

logger = logging.getLogger(__name__)

async def get_cover(params: SearchParams) -> Optional[str]:
    """
    查询并返回封面URL
    """
    title = (params.title or "").strip()
    artist = (params.artist or "").strip()
    album = (params.album or "").strip()
    result = await netease_search(title=title, artist=artist, album=album)
    if not result:
        return None
    return result[0].get("cover")
    
async def get_local_cover(params: SearchParams) -> Optional[str]:
    """
    从本地获取封面图片
    """
    EXTS: list[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    _path = (params.path or "").strip()
    if not _path:
        return None

    def _search_cover() -> Optional[str]:
        music_file_path = Path(_path)
        parent_dir = music_file_path.parent
        for ext in EXTS:
            cover_file_paths = parent_dir / f"cover{ext}"
            if cover_file_paths.exists():
                return cover_file_paths.as_posix()
        return None

    return await asyncio.to_thread(_search_cover)