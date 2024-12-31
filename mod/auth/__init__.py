from flask import request, render_template_string
from .authentication import require_auth
from . import webui

import logging

logger = logging.getLogger(__name__)

def require_auth_decorator(permission):
    def decorator(func):
        def wrapper(*args, **kwargs):
            auth_result = require_auth(request=request, permission=permission)
            if auth_result == -1:
                logger.error("Unauthorized access: 未经授权的用户请求")
                return render_template_string(webui.error()), 401
            elif auth_result == -2:
                logger.error("Unauthorized access: 您没有为API设置鉴权功能，为了安全起见，有关本地文件修改的功能无法使用。"
                             "具体请查看<https://docs.lrc.cx/docs/deploy/auth>以启用API鉴权功能。")
                return render_template_string(webui.error()), 401
            return func(*args, **kwargs)
        return wrapper
    return decorator
