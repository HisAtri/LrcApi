import random
import string
import time

cookies = {}


class Cookie:
    def __init__(self, key: str):
        self.key = key
        self.expire = int(time.time()) + 86400


def generate_cookie_string(length=64):
    """
    生成指定长度的随机字符串作为Cookie
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def set_cookie(key):
    """
    生成Cookie并设置有效期为一天(86400 seconds)
    key: 秘钥字符串
    """
    global cookies
    cookie_string = generate_cookie_string()
    cookies[cookie_string] = Cookie(key)
    clean_expired_cookies()
    return cookie_string


def cookie_key(cookie_string: str) -> str:
    """
    返回Cookie对应的秘钥
    """
    global cookies
    clean_expired_cookies()
    current_time = int(time.time())

    if cookie_string in cookies and cookies[cookie_string].expire >= current_time:
        return cookies[cookie_string].key
    else:
        return ''


def clean_expired_cookies():
    """
    清理失效的Cookie
    """
    global cookies
    current_time = int(time.time())
    expired_cookies = [cookie for cookie, cookie_class in cookies.items() if cookie_class.expire < current_time]

    for expired_cookie in expired_cookies:
        del cookies[expired_cookie]
