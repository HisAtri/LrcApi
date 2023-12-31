from . import cookie

from mod.args import GlobalArgs


args = GlobalArgs()


# 鉴权函数，在auth_token存在的情况下，对请求进行鉴权
# permission=r 代表最小权限
def require_auth(request, permission='r'):
    user_cookie = request.cookies.get("api_auth_token", "")
    cookie_key = cookie.cookie_key(user_cookie)
    auth_header = request.headers.get('Authorization', False) or request.headers.get('Authentication', False)
    cookie_permission = has_permission(get_permission(cookie_key), permission)
    header_permission = has_permission(get_permission(auth_header), permission)

    if permission == 'r' and not args.auth:
        return 1

    if cookie_permission or header_permission:
        return 1
    else:
        return -1


def get_permission(key: str) -> str:
    """
    获取对应的权限组
    :param key:
    :return:
    """
    if not key:
        return ''
    auth_dict = args.auth
    return auth_dict.get(key, '')


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
        supply_set, require_set = set(supply), set(require)
        return require_set.issubset(supply_set)

