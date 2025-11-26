from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse, RedirectResponse

from controller.cover import get_cover, get_local_cover
from utils.value import SearchParams
from utils.exceptions import CoverImageNotFoundError

router = APIRouter()

@router.get("/cover")
async def cover_api(params: SearchParams = Depends()) -> Response:
    """
    查询并返回封面
    """
    # 优先从本地获取封面
    if local_cover := await get_local_cover(params):
        return FileResponse(local_cover)

    # 其次尝试在线获取，若成功则重定向
    if remote_cover := await get_cover(params):
        return RedirectResponse(url=remote_cover, status_code=302)

    # 均未取得则返回 404
    raise CoverImageNotFoundError()
