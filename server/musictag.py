from fastapi import APIRouter

from controller.tag import write_music_tag
from utils.value import MusicTagRequest

router = APIRouter()


@router.post("/tag")
@router.post("/confirm")
@router.put("/tag")
@router.put("/confirm")
async def music_tag_api(request: MusicTagRequest) -> dict:
    """
    写入音乐标签
    支持 POST 和 PUT 方法，使用 JSON 请求体
    """
    return write_music_tag(request)
