import random
import string
import time
import json

from .crypto import crypto


def generate_cookie_string(length=64) -> str:
    """
    生成指定长度的随机字符串作为Cookie
    """
    characters: str = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def set_cookie(key: str) -> str:
    """
    生成Cookie并设置有效期为一天(86400 seconds)
    key: 秘钥字符串
    """
    now: float = time.time()
    plain_text: str = json.dumps({'key': key, 'expire': now + 86400})
    return crypto.encrypt(plain_text)


def cookie_key(cookie_string: str) -> str:
    """
    返回Cookie对应的密码
    """
    current_time = int(time.time())
    # 解密
    plain_text = crypto.decrypt(cookie_string)
    # 解析JSON
    try:
        data = json.loads(plain_text)
    except json.JSONDecodeError:
        return ''
    # 检查Cookie是否过期
    if current_time > data.get('expire', 0):
        return ''
    return data.get('key')
