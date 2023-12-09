import random
import string
import time

cookies = {}


def generate_cookie_string(length=64):
    """
    生成指定长度的随机字符串作为Cookie
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def set_cookie():
    """
    生成Cookie并设置有效期为一天(86400 seconds)
    """
    global cookies
    now = int(time.time())
    cookie_string = generate_cookie_string()
    cookies[cookie_string] = now + 86400
    clean_expired_cookies()
    return cookie_string


def check_cookie(cookie_string: str) -> bool:
    """
    检查Cookie的有效性
    """
    global cookies
    clean_expired_cookies()
    current_time = int(time.time())

    if cookie_string in cookies and cookies[cookie_string] >= current_time:
        return True
    else:
        return False


def clean_expired_cookies():
    """
    清理失效的Cookie
    """
    global cookies
    current_time = int(time.time())
    expired_cookies = [cookie for cookie, expiration_time in cookies.items() if expiration_time < current_time]

    for expired_cookie in expired_cookies:
        del cookies[expired_cookie]
