"""
认证模块 - 用于验证请求头中的 Authorization
"""
from typing import Optional

from fastapi import Header

from utils.config import get_config
from utils.exceptions import UnauthorizedRequestError


async def require_auth(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    依赖注入
    """
    config = get_config()
    
    # 如果未配置 auth，则跳过
    if not config.auth:
        return None
    
    # 验证 Authorization Header
    if not authorization:
        raise UnauthorizedRequestError()
    
    # 支持Bearer token和直接token两种格式
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    
    if token != config.auth:
        raise UnauthorizedRequestError()
    
    return token
