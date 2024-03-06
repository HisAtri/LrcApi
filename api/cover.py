from . import *

import requests

from flask import request, abort, redirect


# 跟踪重定向
def follow_redirects(url, max_redirects=10):
    for _ in range(max_redirects):
        response = requests.head(url, allow_redirects=False)
        if response.status_code == 200:
            return url
        elif 300 <= response.status_code < 400:
            url = response.headers['Location']
        else:
            abort(404)  # 或者根据需求选择其他状态码
    abort(404)  # 达到最大重定向次数仍未获得 200 状态码，放弃


@app.route('/cover', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def cover_api():
    req_args = {key: request.args.get(key) for key in request.args}
    # 构建目标URL
    target_url = 'http://api.lrc.cx/cover?' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    """
    # 跟踪重定向并获取最终URL
    final_url = follow_redirects(target_url)
    # 获取最终URL的内容或响应
    response = requests.get(final_url)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        return Response(response.content, content_type=content_type)
    else:
        abort(404)
    """
    return redirect(target_url, 302)


@v1_bp.route('/cover/<path:s_type>', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def cover_new(s_type):
    __endpoints__ = ["music", "album", "artist"]
    if s_type not in __endpoints__:
        abort(404)
    req_args = {key: request.args.get(key) for key in request.args}
    target_url = f'http://api.lrc.cx/cover/{s_type}/' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    return redirect(target_url, 302)
