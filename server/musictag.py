from fastapi import APIRouter, Depends

from controller.tag import write_music_tag
from utils.value import MusicTagRequest
from utils.authorization import require_auth
router = APIRouter()


@router.post("/tag")
@router.post("/confirm")
@router.put("/tag")
@router.put("/confirm")
async def music_tag_api(request: MusicTagRequest, auth: str = Depends(require_auth)) -> dict:
    """
    写入音乐标签
    支持 POST 和 PUT 方法，使用 JSON 请求体
    """
    return write_music_tag(request)
