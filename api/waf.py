"""
WAF基本防火墙，承担基本的防火墙功能
防注入/恶意文件读取
"""
from api import *

import re
from flask import request, abort


@app.before_request
def check():
    """
    检查请求是否合法
    :return:
    """
    # 获取请求的URL的路径+参数部分，不包括域名
    path = request.path
    if waf(path):
        logger.warning(f"检测到恶意请求: {path}")
        abort(403)


def waf(req: str):
    """
    :param req:
    :return:
    """
    NN_RULES = r"""\.\./
\:\$
\$\{
[\\/]proc[\\/]self[\\/](environ|cmdline|maps)
(?i)select.+(from|limit)
(?i)d(?:elete|rop|ump).+table
(?:(union(.*?)select))
having|rongjitest
sleep\((\s*)(\d*)(\s*)\)
benchmark\((.*)\,(.*)\)
base64_decode\(
(?:from\W+information_schema\W)
(?:(?:current_)user|database|schema|connection_id)\s*\(
(?:etc\/\W*passwd)
into(\s+)+(?:dump|out)file\s*
group\s+by.+\(
xwork.MethodAccessor
xwork\.MethodAccessor
(gopher|doc|php|glob|file|phar|zlib|ftp|ldap|dict|ogg|data)\:\/
java\.lang
\$_(GET|post|cookie|files|session|env|phplib|GLOBALS|SERVER)\[
\<(iframe|script|body|img|layer|div|meta|style|base|object|input)
(onmouseover|onerror|onload)\=
\.\./\.\./
/\*
\:\$
\$\{
(?:define|eval|file_get_contents|include|require|require_once|shell_exec|phpinfo|system|passthru|char|chr|preg_\w+|execute|echo|print|print_r|var_dump|(fp)open|alert|showmodaldialog)\(
\$_(GET|post|cookie|files|session|env|phplib|GLOBALS|SERVER)\[
\s+(or|xor|and)\s+.*(=|<|>|'|")
(?i)select.+(from|limit)
(?:(union(.*?)select))
sleep\((\s*)(\d*)(\s*)\)
benchmark\((.*)\,(.*)\)
(?:from\W+information_schema\W)
(?:(?:current_)user|database|schema|connection_id)\s*\(
into(\s+)+(?:dump|out)file\s*
group\s+by.+\(
\<(iframe|script|body|img|layer|div|meta|style|base|object|input)
@eval.*GET(.*])"""
    for re_str in NN_RULES.split("\n"):
        if re.search(re_str, req):
            # 匹配到恶意请求
            logger.warning(f"匹配规则: {re_str}")
            return True
    # 测试集均为恶意请求，返回False意味着存在漏报
    return False


def test():
    DATAS = [
        "/../../",  # 目录穿越
        "/proc/self/maps",  # 读取系统信息
        "/etc/passwd",  # 读取密码文件
        "/etc/shadow",  # 读取密码文件
        "php://input",  # PHP流协议
        "SELECT * FROM",  # SQL注入
        "DROP TABLE",  # SQL注入
        "SeleCt * fRoM",  # SQL注入，大小写混合
        "sleep(3)",  # SQL注入
        "@@version",  # SQL注入
        "S%e%l%e%c%t * F%rom",  # SQL注入，百分号编码
    ]
    for data in DATAS:
        if not waf(data):
            print(f"有恶意请求未被拦截: {data}")


if __name__ == "__main__":
    test()
