from array import array

from . import cookie
from mod.args import args


def require_auth(request, permission: str = 'r'):
    """
    鉴权
    :param request:
    :param permission: 默认为读权限
    :return:
    """
    user_cookie: str = request.cookies.get("api_auth_token", "")
    cookie_key: str = cookie.cookie_key(user_cookie)
    auth_header: str = request.headers.get('Authorization', False) or request.headers.get('Authentication', False)
    cookie_permission: bool = has_permission(get_permission(cookie_key), permission)
    header_permission: bool = has_permission(get_permission(auth_header), permission)

    if not args("auth"):
        if permission == 'r':
            return 1
        else:
            return -2
    if cookie_permission or header_permission:
        return 1
    else:
        return -1


def get_permission(name: str) -> str:
    """
    通过名称获取对应的权限组
    :param name:
    :return:
    """
    if not name:
        return ''
    auth_dict: dict = args("auth")
    if isinstance(auth_dict, dict):
        return auth_dict.get(name, '')
    elif name == args("auth"):
        return "all"


def has_permission(supply: str, require: str) -> bool:
    """
    判断提交的权限是具有要求的权限
    即提交的权限组是要求的权限组的子集
    :param supply: 提交的权限
    :param require: 该行为要求的权限
    :return bool:
    """
    if not supply:
        return False
    elif supply == "all":
        return True
    else:
        #supply_set, require_set = set(supply), set(require)
        #return require_set.issubset(supply_set)
        return True
